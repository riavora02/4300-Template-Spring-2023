import json
import os
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

def sqlalchemy_search():
    #webtoons = [webtoon.simple_serialize() for webtoon in Webtoon.query.all()]
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
