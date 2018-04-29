from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'connect_to_mongo'
#app.config['MONGO_URI'] = 

mongo = PyMongo(app)

@app.route('/add')
def add():
	user = mongo.db.users
	user.insert({'name' : 'KayceMcCue'})
	return 'Added User!'

@app.route('/find')
def find():
	user = mongo.db.users
	found = user.find_one({'name' : 'KayceMcCue'})
	return 'You found ' + found['name']

if __name__ == '__main__':
	app.run(debug=True)
