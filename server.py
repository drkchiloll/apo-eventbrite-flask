from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from eventbrite import Eventbrite
import requests
import json
import os

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PW = os.environ.get('POSTGRES_PW')
POSTGRES_URL = os.environ.get('POSTGRES_URL')
EVENTBRITE_API_TOKEN = os.environ.get('EVENTBRITE_API_TOKEN') 
postgre_uri = f'postgres://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/evtbrite'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = postgre_uri
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

eventbrite = Eventbrite(EVENTBRITE_API_TOKEN)

class Event(db.Model):
  id = db.Column(db.BigInteger, primary_key=True)
  name = db.Column(db.String(120), unique=True, nullable=False)
  start = db.Column(db.String(80), nullable=False)
  end = db.Column(db.String(80), nullable=False)
  timezone = db.Column(db.String(80), nullable=False)
  description = db.Column(db.String(8000), nullable=True)
  logo_id = db.Column(db.BigInteger)
  logo_url = db.Column(db.String(8000), unique=True, nullable=True)
  category_id = db.Column(db.BigInteger)
  subcategory_id = db.Column(db.BigInteger)
  venue_address = db.Column(db.String(2000), nullable=True)

  def __repr__(self):
    return '<Event %r>' % self.name

@app.route('/categories')
def get_categories():
  return eventbrite.get('/categories')

@app.route('/events', methods=['GET', 'POST'])
def event_task():
  if request.method == 'GET':
    try:
      r = requests.get('http://localhost:8012/api/events')
      return r.json()
    except:
      return '0'
  elif request.method == 'POST':
    event = json.loads(request.data)
    item = Event(
      id=event['id'],
      name=event['name'],
      start=event['start'],
      end=event['end'],
      timezone=event['timezone'],
      description=event['description'],
      logo_id=event['logoId'],
      logo_url=event['logoUrl'],
      category_id=event['categoryId'],
      subcategory_id=event['subcategoryId'],
      venue_address=event['venueAddress']
    )
    db.session.add(item)
    db.session.commit()
  return json.dumps(event)

@app.route('/events/<id>', methods=['DELETE'])
def get_one(id):
  event = Event.query.get(id)
  db.session.delete(event)
  db.session.commit()
  return '0'

@app.route('/events/saved')
def get_saved():
  r = requests.get('http://localhost:8012/api/events/saved')
  return r.json()

@app.route('/event/search', methods=['POST'])
def search_events():
  search = json.loads(request.data)
  print(search)
  r = requests.post('http://localhost:8012/api/event/search', data=search) 
  return r.json()
