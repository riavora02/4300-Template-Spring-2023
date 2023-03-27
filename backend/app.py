import json
import os
from sklearn import TfidfVectorizer 
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import Webtoon, MySQLDatabaseHandler, db
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = ""
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

#SQLAlchemy setup stuff
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{mysql_engine.MYSQL_USER}:{mysql_engine.MYSQL_USER_PASSWORD}@{mysql_engine.MYSQL_HOST}:{mysql_engine.MYSQL_PORT}/{mysql_engine.MYSQL_DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(error, code=404):
    return json.dumps({"error": error}), code 

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
# TODO: use SQLAlchemy instead of these raw queries
# def sql_search():
#     query_sql = f"""SELECT * FROM webtoons limit 10"""
#     keys = ["id", "webtoon_id", "title", "genre", "thumbnail", "summary"]
#     data = mysql_engine.query_selector(query_sql)
#     print(data)
#     return json.dumps([dict(zip(keys,i)) for i in data])

def webtoon_name_array(data):
    webtoon_to_index = {}
    index = 0
    for webtoon in data:
        title = webtoon["title"]
        webtoon_to_index[title] = index
        index += 1


def unique_words(data):
    """Finds all the unique words in the webtoon summaries"""
    unique = set()
    for webtoon in data:
        summary = webtoon["summary"]
        tokened = set(summary.split())
        unique = unique.union(tokened)


def webtoon_tfdi(data, max_df=0.8, min_df=10, norm='l2',):
    """word_count is the total number of unique words in the summaries,
and data is the data from kaggle"""
    word_count = unique_words(data)
    vector = TfidfVectorizer(max_features=word_count,
                             max_df=max_df,
                             min_df=min_df,
                             stop_words="english",
                             norm=norm
                             )
    doc_by_vocab = vector.fit_transform([d['summary'] for d in data]).toarray()
    return doc_by_vocab


def get_cossim(query, wt, data):
    matrix = webtoon_tfdi(data)
    webtoon_to_index = webtoon_name_array(data)
    q = matrix[webtoon_to_index[wt1]]
    wt_ind = matrix[webtoon_to_index[wt]]
    num = np.dot(wt1_ind, mov2_ind)
    den = np.dot(np.linalg.norm(wt1_ind), np.linalg.norm(mov2_ind))

    return num/den

def sqlalchemy_search():
    summaries = [webtoon.simple_serialize()["summary"] for webtoon in Webtoon.query.all()]
    query_input = request.args.get("q")
    webtoons = Webtoon.query.all()
    cosine_scores = {}
    for w in Webtoon.query.all():
        webtoon_data = w.simple_serialize()
        cosine_scores[w] = get_cossim(query_input,w,webtoon_data["summary"])
    out = sorted(cosine_scores.items(), key = lambda x: x[1], reverse = True)
    webtoons = [webtoon.simple_serialize() for webtoon in out.keys()[:11]]
    return success_response({"webtoons": webtoons})

@app.route("/")
def home():
    return render_template('base.html', title="sample html")

@app.route("/webtoons")
def webtoon_search():
    # text = request.args.get("title")
    return sqlalchemy_search()

# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_search(text)

# if __name__ == "__main__":
#     app.run(debug=True)
