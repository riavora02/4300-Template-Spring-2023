from helpers.MySQLDatabaseHandler import Webtoon, MySQLDatabaseHandler, db
import numpy as np
import re
from nltk.tokenize import TreebankWordTokenizer
from sklearn.feature_extraction.text import CountVectorizer

def tokenize(text):
    return [x for x in re.findall(r"[a-z]+", text.lower())]

def preprocess(): 

     webtoons = [webtoon.simple_serialize() for webtoon in Webtoon.query.all()]

     # the labels here are the genres
     # genre_mappings maps each genre to an index
     # genre_count gives probability of webtoon in that genre P(label = y)

     genre_mappings = {}
     summary_lst = []
     webtoon_num_to_genre = {}
     count = 0

     for webtoon in webtoons: 

          if webtoon['genre'] not in genre_mappings: 
               genre_mappings[webtoon['genre']] = len(genre_mappings)

          webtoon_num_to_genre[count] = webtoon['genre']
          count += 1

          summary_lst.append(webtoon["summary"])

     vectorizer = CountVectorizer(max_df=0.7, min_df=1)
     vectors = vectorizer.fit_transform(summary_lst).toarray()
     features = vectorizer.get_feature_names()
     
     for line in vectors: 
          print(sum(line))
     print(features)
     print(len(vectors))

     genre_count = np.zeros(len(genre_mappings))
     for webtoon in webtoons: 
          index = genre_mappings[webtoon['genre']]
          genre_count[index] += 1

     for i in range(len(genre_count)): 
          genre_count[i] /= len(webtoons)