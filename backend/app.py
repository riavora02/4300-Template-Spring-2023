import json
import os
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer 
import nltk
from nltk.tokenize import TreebankWordTokenizer
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
treebank_tokenizer = TreebankWordTokenizer()
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
    doc_by_vocab = vector.fit_transform([d for d in data]).toarray()
    return doc_by_vocab

def inverted_index(data):
    inv_index = {}
    for id,summary in enumerate(data):
        tokens = list(nltk.word_tokenize(summary))
        for word in set(tokens):
            if word not in inv_index:
                inv_index[word]=[(id,tokens.count(word))]
            else:
                inv_index[word].append((id,tokens.count(word)))
    return inv_index

def compute_idf(inv_idx, n_docs, min_df=10, max_df_ratio=0.95):
    idf = {}
    for word in inv_idx:
        df = len(inv_idx[word])
        if df<min_df or (df/n_docs)>max_df_ratio:
            pass
        else:
            idf[word]=math.log(n_docs/(df+1),2)
    return idf

def compute_norm(index,idf,n_docs):
    norms = np.zeros(n_docs)
    sum = [0]*n_docs
    for word in index:
        df = len(index[word])
        if word in idf:
            for j in index[word]:
                sum[j[0]]+=(j[1]*idf[word])**2
    for i in range(n_docs):
        norms[i]=math.sqrt(sum[i])
    return norms

def acc_dot_score(query_word_counts, index, idf):
    doc_scores = {}
    for word in query_word_counts:
        if word in idf:
            for i in index[word]:
                if i[0] not in doc_scores:
                    doc_scores[i[0]]=idf[word]*query_word_counts[word]*i[1]*idf[word]
                else:
                    doc_scores[i[0]]+=idf[word]*query_word_counts[word]*i[1]*idf[word]
    return doc_scores

def get_cossim(query, index, idf, doc_norms, wt, score_func=acc_dot_score, tokenizer=treebank_tokenizer):

    inv_idx = inverted_index(data)
    idf = compute_idf(inv_idx, len(data),min_df=10,max_df_ratio=0.1) 
    inv_idx = {key: val for key, val in inv_idx.items() if key in idf}
    doc_norms = compute_norm(inv_idx, idf, len(data)) 
    
    query = query.lower()
    tokens = tokenizer.tokenize(query)
    n_docs = len(doc_norms)
    
    query_dict = {}
    
    results = []
    sum = 0
    for word in tokens:
        if word not in query_dict:
            query_dict[word]=1
        else:
            query_dict[word]+=1
    
    for word in query_dict:
        if word in idf:
            sum+=(query_dict[word]*idf[word])**2
        
    query_norm = math.sqrt(sum)
 
    doc_scores = score_func(query_dict,index,idf)
    score = 0
    for i in doc_scores:
        score = doc_scores[i]/(query_norm*doc_norms[i])
        results.append((score,i))
    
    #return sorted(results,key=lambda x:x[0],reverse=True)
    
    matrix = webtoon_tfdi(data)
    webtoon_to_index = webtoon_name_array(data)
    q = webtoon_tfdi(q)
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
