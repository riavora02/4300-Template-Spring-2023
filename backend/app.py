import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import Webtoon, MySQLDatabaseHandler, db
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from nltk.tokenize import TreebankWordTokenizer


# db = SQLAlchemy()

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = ""
MYSQL_PORT = 3306
MYSQL_DATABASE = "kardashiandb"

mysql_engine = MySQLDatabaseHandler(
    MYSQL_USER, MYSQL_USER_PASSWORD, MYSQL_PORT, MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# SQLAlchemy setup stuff
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
    webtoons = [webtoon.simple_serialize() for webtoon in Webtoon.query.all()]
    return success_response({"webtoons": webtoons})


@app.route("/")
def home():
    return render_template('base.html', title="sample html")


@app.route("/webtoons")
def webtoon_search():
    # text = request.args.get("title")
    return sqlalchemy_search()


# data = [{"title": "Let's Play", "summary": "young, single and about to achieve her dream of creating incredible videogames. But then life throws her a one-two punch: a popular streamer gives her first game a scathing review. Even worse she finds out that same troublesome critic is now her new neighbor!  A funny, sexy and all-too-real story about gaming, memes and social anxiety. Come for the plot, stay for the doggo."},
#         {"title": "True Beauty", "summary": "After binge-watching beauty videos online, a shy comic book fan masters the art of makeup and sees her social standing skyrocket as she becomes her schoolâ€™s prettiest pretty girl overnight. But will her elite status be short-lived? How long can she keep her real self a secret? And what about that cute boy who knows her secret?"}]

treebank_tokenizer = TreebankWordTokenizer()


def tokenize(text):
    return [x for x in re.findall(r"[a-z]+", text.lower())]


def build_inverted_index(data):
    """ Builds an inverted index from the messages.
    """
    message_indx = 0
    inverted = {}
    for webtoon in data:
        token_list = tokenize(webtoon['summary'])
        for token in token_list:
            count_tok = token_list.count(token)

            if token in inverted:
                inverted[token] += [(message_indx, count_tok)]

            else:
                inverted[token] = [(message_indx, count_tok)]
        message_indx += 1
    for term in inverted:
        new = [*set(inverted[term])]
        sorted_list = sorted(new, key=lambda x: x[0])
        inverted[term] = sorted_list
    return inverted


def compute_idf(inv_idx, n_docs, min_df=10, max_df_ratio=0.95):
    """ Compute term IDF values from the inverted index.
    Words that are too frequent or too infrequent get pruned.
    """
    term_idf_dict = {}
    for term in inv_idx:
        number_of_docs = len(inv_idx[term])
        if (number_of_docs/n_docs) < max_df_ratio and number_of_docs > min_df:
            term_idf = np.log2(n_docs/(1+number_of_docs))
            term_idf_dict[term] = term_idf
    return term_idf_dict


def compute_doc_norms(index, idf, n_docs):
    """ Precompute the euclidean norm of each document."""
    norms = np.zeros(n_docs)
    term_freq = {}
    for term in index:
        term = term.lower()
        if term in idf:
            idf_value = idf[term]
        else:
            idf_value = 0
        for doc_tf in index[term]:
            doc_num = doc_tf[0]
            norms[doc_tf[0]] += (doc_tf[1] * idf_value)**2
    return np.sqrt(norms)


def accumulate_dot_scores(query_word_counts, index, idf):
    """ Perform a term-at-a-time iteration to efficiently compute the numerator term of cosine similarity across multiple documents."""

    doc_scores = {}
    for term in query_word_counts:
        if query_word_counts[term] != 0 or idf[term] != 0:

            for x, y in index[term]:
                if x not in doc_scores:
                    doc_scores[x] = 0
                dij = y * idf[term]
                qi = query_word_counts[term] * idf[term]
                doc_scores[x] += qi * dij

#     print(doc_scores[324])
    return doc_scores


inv_idx = build_inverted_index(data)
idf = compute_idf(inv_idx, len(data),
                  min_df=10,
                  max_df_ratio=0.1)  # documents are very short so we can use a small value here
# examine the actual DF values of common words like "the"
# to set these values
inv_idx = {key: val for key, val in inv_idx.items()
           if key in idf}            # prune the terms left out by idf
doc_norms = compute_doc_norms(inv_idx, idf, len(data))


def index_search(query, index, idf, doc_norms, score_func=accumulate_dot_scores, tokenizer=treebank_tokenizer):
    """ Search the collection of documents for the given query"""
    indx_search = []
    query = query.lower()
    tokens = tokenizer.tokenize(query)
    query_number = {}
    acc = 0

    for token in tokens:
        if token in idf:
            if token not in query_number:
                query_number[token] = 0
            query_number[token] += 1

    for token in query_number:
        if token in idf:
            acc += (query_number[token] * idf[token])**2
    acc = np.sqrt(acc)

    numerator_terms = score_func(query_number, index, idf)
    print(numerator_terms)
    for x, y in numerator_terms.items():
        indx_search += [(y/(acc * doc_norms[x]), x)]
    indx_search.sort(reverse=True)
    return indx_search


def get_cossim(query):
    results = index_search(query, inv_idx, idf, doc_norms)
    return results


# @app.route("/episodes")
# def episodes_search():
#     text = request.args.get("title")
#     return sql_search(text)

# if __name__ == "__main__":
#     app.run(debug=True)
