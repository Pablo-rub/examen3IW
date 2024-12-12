from datetime import datetime
from flask import Flask, request, redirect, url_for, jsonify
import pymongo
from environs import Env
from bson import ObjectId

app = Flask(__name__)

env = Env()
env.read_env()

uri = env('MONGO_URI')
print("MONGO_URI: ", uri)
client = pymongo.MongoClient(uri)
db = client.examen3IW
events = db.events

# Definicion de metodos para endpoints
@app.route('/', methods=['GET'])
def showEvents():
    all_events = list(events.find().sort('date', pymongo.DESCENDING))
    for event in all_events:
        event['_id'] = str(event['_id'])
    return jsonify({"events": all_events})

@app.route('/new', methods=['POST'])
def newEvent():
    event = {
        'author': request.form['inputAuthor'],
        'text': request.form['inputText'],
        'priority': int(request.form['inputPriority']),
        'date': datetime.now()
    }
    events.insert_one(event)
    return redirect(url_for('showEvents'))

@app.route('/edit/<_id>', methods=['POST'])
def editEvent(_id):
    event = {
        'author': request.form['inputAuthor'],
        'text': request.form['inputText'],
        'priority': int(request.form['inputPriority'])
    }
    events.update_one({'_id': ObjectId(_id)}, {'$set': event})
    return redirect(url_for('showEvents'))

@app.route('/delete/<_id>', methods=['GET'])
def deleteEvent(_id):
    events.delete_one({'_id': ObjectId(_id)})
    return redirect(url_for('showEvents'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
