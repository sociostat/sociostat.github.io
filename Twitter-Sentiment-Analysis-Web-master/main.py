from flask import Flask,render_template,request,jsonify
import json
import logging as log
import re
from textblob import TextBlob
import sys
from abc import ABCMeta, abstractmethod
from json import JSONDecodeError
import bs4
import requests
import pandas as pd
from langdetect import detect
import regex as re


#--------------------------------------------------------------------------

#-------------------------------------------------------------------------

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/search",methods=["POST"])
def search():
	t = []
	search_tweet = request.form.get("search_query")
	url_string = "https://www.instagram.com/explore/tags/%s/" % search_tweet
	response = bs4.BeautifulSoup(requests.get(url_string).text, "html.parser")
	#potential_query_ids = self.get_query_id(response)
	for script_tag in response.find_all("script"):
		if script_tag.text.startswith("window._sharedData ="):
			shared_data = re.sub("^window\._sharedData = ", "", script_tag.text)
			shared_data = re.sub(";$", "", shared_data)
			shared_data = json.loads(shared_data)
	media = shared_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
	for nd in media:
		try:
			post =  nd['node']['edge_media_to_caption']['edges'][0]['node']['text']
			post = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",post).split())
		except:
			pass		
		try:
			if detect(post) == 'en':
				polarity = TextBlob(post).sentiment.polarity
				subjectivity = TextBlob(post).sentiment.subjectivity
				t.append([post])
		except:
			pass
	return jsonify({"success":True,"tweets":t[:10]})

app.run()

