from helpers.MySQLDatabaseHandler import Webtoon, MySQLDatabaseHandler, db
import numpy as np
import re
from nltk.tokenize import TreebankWordTokenizer
from sklearn.feature_extraction.text import CountVectorizer
import os.path
import pickle

def tokenize(text):
    return [x for x in re.findall(r"[a-z]+", text.lower())]


def preprocess(query, n=3): 

     webtoons = [webtoon.simple_serialize() for webtoon in Webtoon.query.all()]

     # the labels here are the genres
     # genre_mappings maps each genre to an index

     genre_mappings = {}
     summary_lst = []
     webtoon_num_to_genre = {}
     count = 0

     for webtoon in webtoons:      

          if webtoon['genre'] not in genre_mappings: 
               genre_mappings[webtoon['genre']] = len(genre_mappings)

          webtoon_num_to_genre[count] = genre_mappings[webtoon['genre']]
          count += 1

          summary_lst.append(webtoon["summary"])

     vectorizer = CountVectorizer(max_df=0.7, min_df=1)

     #vectors is an array where the rows represent webtoon summaries and the columns are words in the corpus
     #dimension of vectors is 734 x num features
     vectors = np.array(vectorizer.fit_transform(summary_lst).toarray())
     features = vectorizer.get_feature_names()

     # genre_count gives probability of webtoon in that genre P(label = y)
     genre_count = np.zeros(len(genre_mappings))
     for webtoon in webtoons: 
          index = genre_mappings[webtoon['genre']]
          genre_count[index] += 1

     for i in range(len(genre_count)): 
          genre_count[i] /= len(webtoons)


     #First we implement Add-1 smoothing so that we don't get non-zero probabilities
     # vectors = vectors + 1

     total_counts = np.sum(vectors, axis = 0)

     if not os.path.exists('prob.txt'):
          # label_word_prob gives probability of word occuring given genre P(X | Y)
          label_word_prob = np.zeros((len(genre_mappings), len(vectors[0])))

          #Now we loop through each of the labels in the corpus and for each of the genres we find the label_word_prob
          for i in range(len(genre_mappings)):
               for word_num in range(len(vectors[0])):
                    sum = 0 
                    for row in range(len(vectors)):
                         sum += vectors[row][word_num] if webtoon_num_to_genre[row] == i else 0
                    label_word_prob[i][word_num] = sum / total_counts[word_num]
          
          pickle.dump(label_word_prob, open("prob.txt", 'wb'))
          
     label_word_prob = pickle.load(open("prob.txt", 'rb'))

     # Now given a query we can iterate through all the genres and see which genre it is most likely to be present in
     query = query.split()
     total_prob_per_label = np.ones((len(genre_mappings)))
     for i in range(len(genre_mappings)):
          for word in query: 
               if word in features: 
                    index = features.index(word)
                    total_prob_per_label[i] *= label_word_prob[i][index]
          total_prob_per_label[i] *= genre_count[i]

     # most_likely = np.argmax(total_prob_per_label)
     # most_likely_genre = ""
     
     most_likely_n = np.argsort(total_prob_per_label)[::-1]
     reverse_genre_mappings = {value: key for key, value in genre_mappings.items()}
     
     top_genres = []
     for idx in most_likely_n:
          top_genres.append(reverse_genre_mappings[idx])

     # for key, value in genre_mappings.items(): 
     #      if value == most_likely: 
     #           most_likely_genre = key
     
     # print(most_likely_genre)
     return top_genres[:n]
     
