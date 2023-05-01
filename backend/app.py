import json
import os
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from nltk.tokenize import TreebankWordTokenizer
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import Webtoon, MySQLDatabaseHandler, db
from bayes import *

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
app.config["SQLALCHEMY_ECHO"] = False


db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(error, code=404):
    return json.dumps({"error": error}), code 


treebank_tokenizer = TreebankWordTokenizer()


def tokenize(text):
    return [x for x in re.findall(r"[a-z]+", text.lower())]


def build_inverted_index(data):
    """ Builds an inverted index from the messages.
    """
    message_indx = 0
    inverted = {}
    web_ind = {}
    for webtoon in data:
        token_list = tokenize(webtoon["summary"])
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
    

def compute_idf(inv_idx, n_docs, min_df=1, max_df_ratio=0.99):
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

    return doc_scores


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
    
    for x, y in numerator_terms.items():
        indx_search += [(y/(acc * doc_norms[x]), x)]
    indx_search.sort(reverse=True)
    return indx_search


def get_cossim(data,query):
    inv_idx = build_inverted_index(data)
    idf = compute_idf(inv_idx, len(data),
                    min_df=10,
                    max_df_ratio=0.1)  # documents are very short so we can use a small value here
    # examine the actual DF values of common words like "the"
    # to set these values
    inv_idx = {key: val for key, val in inv_idx.items()
            if key in idf}            # prune the terms left out by idf
    doc_norms = compute_doc_norms(inv_idx, idf, len(data))
    results = index_search(query, inv_idx, idf, doc_norms)
    return results


def get_svd(query, data, sim_threshold=0.35):
    vec = TfidfVectorizer()
    webtoon_summaries = []
    for i in data:
        webtoon_summaries.append(i["summary"])
    tfidf = vec.fit_transform(webtoon_summaries)
    
    svd = TruncatedSVD(n_components=40)
    docs = svd.fit_transform(tfidf)
    query_tfidf = vec.transform([query])
    query_vec = svd.transform(query_tfidf)
    
    sims = cosine_similarity(query_vec, docs).flatten()
    indices = np.argsort(sims)[::-1]
    indices = [idx for idx in indices if sims[idx] >= sim_threshold]
    items = []
    for idx in indices:
        data[idx]["sim"] = sims[idx]
        items.append(data[idx])
    return items


# def sqlalchemy_search(query_input):
#     webtoons = [webtoon.simple_serialize() for webtoon in Webtoon.query.all()]
#     summary_to_webtoon = {}
#     for i in webtoons:
#         if i["summary"] not in summary_to_webtoon:
#             summary_to_webtoon[i["summary"]]=i["title"]
    
#     output = []
#     #results = get_cossim(webtoons,query_input)
#     results = get_svd(query_input,webtoons)
#     for i in range(len(results)):
#         output.append(webtoons[results[i][1]])
#     return success_response({"webtoons": output[:10]})


def get_svd_results(query_input, desired_percentile):
    webtoons = [webtoon.likes_serialize() for webtoon in Webtoon.query.all()]
    summary_to_webtoon = {}
    for i in webtoons:
        if i["summary"] not in summary_to_webtoon:
            summary_to_webtoon[i["summary"]]=i["title"]
    
    results = sorted(get_svd(query_input, webtoons), key=lambda webtoon: webtoon["social"])
    return calculate_percentile(results, desired_percentile)


def custom_search(query_input, likely_genres, desired_percentile):
    output = get_svd_results(query_input, desired_percentile)
    output = [w for w in output if w["genre"] in likely_genres]
    return output[:10]


def calculate_percentile(webtoon_dict, desired_percentile):
    """
    This function assumes webtoon_dict is sorted
    """
    #adds the percentile to every webtoon
    for i in range(len(webtoon_dict)):
        num_below = webtoon_dict[i+1:]
        percentile = (len(num_below) / len(webtoon_dict))*100
        webtoon_dict[i]["percentile"] = percentile  
    # print(webtoon_dict) 
    #returns the list in the right order 
    webtoon_dict.sort(key = lambda wtoon: abs(wtoon["percentile"] - desired_percentile))
    return webtoon_dict


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/webtoons")
def webtoon_search():
    query_input = request.args.get("q")
    user_genre = request.args.get("genre")
    filter_num = int(request.args.get("num") if request.args.get("num") else 100)
    likely_genres = preprocess(query_input)
    if query_input:
        if user_genre == "all":
            return success_response({"all": get_svd_results(query_input, filter_num), "webtoons": custom_search(query_input, likely_genres, filter_num)})
        else:
            return success_response({"all": custom_search(query_input, [user_genre], filter_num), "webtoons": custom_search(query_input, likely_genres, filter_num)})
    else:
        output = sorted([webtoon.likes_serialize() for webtoon in Webtoon.query.all()], key=lambda webtoon: webtoon["social"])
        return success_response({"webtoons": calculate_percentile(output, filter_num)})
    
    
@app.route("/genres")
def get_genres():
    res = Webtoon.query.with_entities(Webtoon.genre).distinct().all()
    return success_response({"genres": [genre[0] for genre in res]})


if __name__ == "__main__":
    app.run(debug=True)
