from flask import Flask, render_template, url_for, request
import json
import logging as log
import re
import sys
from flask import jsonify
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError
import bs4
import requests
import pandas as pd
from langdetect import detect
import regex as re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from nltk import FreqDist, classify, NaiveBayesClassifier
import joblib
import re, string, random
app = Flask(__name__)

import joblib
classifier = joblib.load('text_analyzer')

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


@app.route('/<query>')
def index(query):
		posts=[]
		sentim=[]
		num=[]
		url_string = "https://www.instagram.com/explore/tags/%s/" % query
		response = bs4.BeautifulSoup(requests.get(url_string).text, "html.parser")		
		for script_tag in response.find_all("script"):
			if script_tag.text.startswith("window._sharedData ="):
				shared_data = re.sub("^window\._sharedData = ", "", script_tag.text)
				shared_data = re.sub(";$", "", shared_data)
				shared_data = json.loads(shared_data)
		try:
			media = shared_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
			for nd in media:
				post =  nd['node']['edge_media_to_caption']['edges'][0]['node']['text']
				post = ' '.join(re.sub("(#[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",post).split())
				try:
					if detect(post) == 'en' and post not in posts:
						posts.append(post)
						if TextBlob(post).sentiment.polarity <0:
							sentiment = 'negative'
						elif TextBlob(post).sentiment.polarity >0:
							sentiment = 'positive'
						else:
							sentiment = 'neutral'
						sentim.append(classifier.classify(dict([token, True] for token in remove_noise(word_tokenize(post)))))

				except:					
					pass
		except:
			for i in range(0,15):
				posts.append('Nothing found')
				sentim.append('No ')
		for i in range(len(posts)):
			num.append(i)
		l1 = list(zip(posts,sentim,num))
		diction = dict(list(zip(posts,sentim)))
		return jsonify(diction)

if __name__ == "__main__":
	app.run(debug=True)
