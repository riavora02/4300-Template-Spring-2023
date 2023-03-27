import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "MayankRao16Cornell.edu"
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


def sql_search(episode):
    query_sql = f"""SELECT * FROM episodes WHERE LOWER( title ) LIKE '%%{episode.lower()}%%' limit 10"""
    keys = ["id", "title", "descr"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


# assumes data will be in form of [{id: value, title: value, genre:value...}, {id: value, title: value, genre:value...} ]
# name to index of webtoon, in order as given on kaggle

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
    doc_by_vocab = vector.fit_transform([d['script'] for d in data]).toarray()
    return doc_by_vocab


def get_cossim(wt1, wt2, data):
    matrix = webtoon_tfdi(data)
    webtoon_to_index = webtoon_name_array(data)
    wt1_ind = matrix[webtoon_to_index[wt1]]
    mov2_ind = matrix[webtoon_to_index[wt2]]
    num = np.dot(wt1_ind, mov2_ind)
    den = np.dot(np.linalg.norm(wt1_ind), np.linalg.norm(mov2_ind))

    return num/den


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/episodes")
def episodes_search():
    text = request.args.get("title")
    return sql_search(text)

# app.run(debug=True)
