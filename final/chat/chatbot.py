from flask import Flask, render_template, request, jsonify
import random
import json
import pickle
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import nltk

chatbot = Flask(__name__)

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('C:\\Users\\my lapi\\Desktop\\SIMPLE-CHATBOT\\final\\chat\\intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = [{'intent': classes[r[0]], 'probability': str(r[1])} for r in results]
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

@chatbot.route("/")
def home():
    return render_template("interface.html")

@chatbot.route("/get_response", methods=["POST"])
def chatbot_response():
    message = request.json.get("message")
    intents_list = predict_class(message)
    response = get_response(intents_list, intents)
    return jsonify({"response": response})

if __name__ == "__main__":
    chatbot.run(debug=True, port= 5000)
