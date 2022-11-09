import flask
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pint import UnitRegistry
from flask import Flask, jsonify, request
import spacy
import torch
import pint


import nltk

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')


app = Flask(__name__)


###################################################

def find_missing(elements):
    idx = 0
    tofind = ' '
    for i in range(len(elements)):
        if not elements[i].isnumeric():
            idx = i
            tofind = elements[i]
            break
    if idx == 2:
        return int(elements[1]) / int(elements[0])
    elif idx == 1:
        return int(elements[2]) * int(elements[0])
    elif idx == 0:
        return int(elements[1]) / int(elements[2])


def Process(phrase):
    ureg = UnitRegistry()
    stop_words = stopwords.words('english')

    words = word_tokenize(phrase)
    stripped_phrase = []
    for word in words:
        if word not in stop_words:
            stripped_phrase.append(word)

    listToStr = ' '.join([str(elem) for elem in stripped_phrase])

    tb_phrase = TextBlob(listToStr)
    a = tb_phrase.tags

    speed = 0
    time = 0
    distance = 0
    i = 1
    for word in a:
        if i == len(a)+1:
            break

        if word[1] == "CD":

            value = int(word[0])
            unit = (a[i][0])
            decide = int(value) * ureg(unit)

            if decide.dimensionality == '[length] / [time]' or decide.dimensionality == '[time] / [length] / [mass]':
                speed = decide
            elif decide.dimensionality == '[length]':
                distance = decide
                distance = (distance.to(ureg.kilometer))
            elif decide.dimensionality == '[time]':
                time = decide
                time = (time.to(ureg.hour))

        i = i+1

    try:
        d = str(int(distance.magnitude))
    except:
        d = "empty"
        ext = "km"

    try:
        s = str(int(speed.magnitude))
    except:
        s = "empty"
        ext = "kmph"

    try:
        t = str(int(time.magnitude))
    except:
        t = "empty"
        ext = "hours"

    stringtest = [str(s), str(d), str(t)]
    return str((find_missing(stringtest))) + " "+ext

###################################################


@app.route('/')
def index():
    return flask.redirect(flask.url_for('home'))


@app.route('/home')
def home():
    return flask.render_template('index.html')


@app.route('/solve', methods=['GET', 'POST'])
def solve():
    if flask.request.method == 'POST':
        return flask.render_template('solve.html', final_value=Process(request.form.to_dict()['question_text']))
    else:
        return flask.redirect(flask.url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
