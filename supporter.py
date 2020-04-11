import warnings
warnings.filterwarnings("ignore")
import flair
from flair.models import TextClassifier
from flair.data import Sentence
classifier = TextClassifier.load('en-sentiment')

def sentimentAnalysis(inputQuery):
	sentence = Sentence(inputQuery)
	classifier.predict(sentence)
	label = sentence.labels[0]
	labscore = (label.score)*100
	response = {'result': label.value, 'score':"%.2f" % labscore}
	return sentence.labels
