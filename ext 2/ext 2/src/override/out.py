import config

from flask import Flask, redirect, url_for, request, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = config.dbName()
app.config['MONGO_URI'] = config.mongoURI()

mongo = PyMongo(app)

import http.client
import json

@app.route('/success/<name>')
def success(name):
    return 'Jobs: %s' % name

@app.route('/search',methods = ['POST', 'GET'])
def search():
    host = 'us.jooble.org'
    key = config.apiKey()

    connection = http.client.HTTPConnection(host)
    #request headers
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    if request.method == 'POST':
        user = request.form['keyword']
        loc = request.form['location']
    else:
        user = request.args.get('keyword')
        loc = request.args.get('location')
    
    dbUser = mongo.db.users
    jobs = []

    if(dbUser.count({'keyword' : user, 'location' : loc}) > 0):
        found = dbUser.find_one({'keyword' : user, 'location' : loc})
        jobs = found['jobs']
        print('cache') #Indicates that this has been search before and it is found in the db
    else:
        body = '{ "keywords": "' + user + '", "location": "' + loc + '"}'
        connection.request('POST','/api/' + key, body, headers)
        response = connection.getresponse()
        j = response.read()
        j = json.loads(j)
        j.update({'keyword' : user, 'location' : loc})
        jobs = j['jobs']
        dbUser.insert(j)
        print('new') #Indicates that this is a new search 

    max = 5
    if len(jobs) < 5:
        max = len(jobs)
    for i in range(0,max):
        fstJob = jobs[i]
        if(i == 0):
            user = fstJob["company"]
        elif(i == max-1):
            user += ', and ' + fstJob["company"] + '.'
        else:
            user += ', ' + fstJob["company"]
    return redirect(url_for('success',name = user))
    #return redirect(url_for('emails',name = user))
    #return render_template('results.html', email_addresses=user)

@app.route('/')
def hello_world():
    author = "Me"
    name = "You"
    return render_template('index.html', author=author, name=name)

if __name__ == '__main__':
    app.run(debug = True)