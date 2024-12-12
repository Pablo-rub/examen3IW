import pymongo

from environs import Env
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

env = Env()
env.read_env()  # read .env file, if it exists

uri = env('MONGO_URI')

print("MONGO_URI: ",uri)

client = pymongo.MongoClient(uri)

db = client.examen3IW   # db = client['examen3IW']

events = db.events      # events = db['events']

# Definicion de metodos para endpoints

@app.route('/', methods=['GET'])
def showEvents():
    
    return render_template('events.html', events=list(events.find().sort('date', pymongo.DESCENDING)))
    
@app.route('/new', methods=['GET', 'POST'])
def newEvent():

    if request.method == 'GET':
        return render_template('new.html')
    else:
        event = {'author': request.form['inputAuthor'],
                 'text': request.form['inputText'], 
                 'priority': int(request.form['inputPriority']),
                 'date': datetime.now()
                }
        events.insert_one(event)
        return redirect(url_for('showEvents'))

@app.route('/edit/<_id>', methods=['GET', 'POST'])
def editEvent(_id):
    
    if request.method == 'GET':
        event = events.find_one({'_id': ObjectId(_id)})
        return render_template('edit.html', event=event)
    else:
        event = {'author': request.form['inputAuthor'],
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
    app.run(host='127.0.0.1', port=8000, debug=True)
