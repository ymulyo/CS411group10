import config

from flask import Flask, redirect, url_for, request, render_template, render_template, session, jsonify
from flask_pymongo import PyMongo
from flask_oauthlib.client import OAuth
from datetime import datetime

import bcrypt

app = Flask(__name__)
app.config['MONGO_DBNAME'] = config.dbName()
app.config['MONGO_URI'] = config.mongoURI()

oauth = OAuth(app)

mongo = PyMongo(app)



import http.client
import json

hashpass = ''

linkedin = oauth.remote_app(
    'linkedin',
    consumer_key= config.consumerKey(),
    consumer_secret= config.consumerSecret(),
    request_token_params={
        'scope': 'r_basicprofile',
        'scope': 'r_emailaddress',
        'scope': 'rw_company_admin',
        'scope': 'w_share',
        'state': 'DCEEFWF45453sdffef424',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)

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
    found = dbUser.find_one({'keyword' : user, 'location' : loc})
    if found:
        if 'username' in found:
            if 'username' in session and not(session['username'] in found['username']):
                found['username'].append(session['username'])
            elif(not('guest' in found['username']) and not('username' in session)):
                found['username'].append('guest')
        else:
            name = ''
            if not('username' in session):
                name = 'guest'
            else: 
                name = found['username']
            found.update({'username' : [name]})
        jobs = found['jobs']
        print('cache') #Indicates that this has been search before and it is found in the db:
            
    else:
        body = '{ "keywords": "' + user + '", "location": "' + loc + '"}'
        connection.request('POST','/api/' + key, body, headers)
        response = connection.getresponse()
        j = response.read()
        j = json.loads(j)
        name = ''
        if not('username' in session):
            name = 'guest'
        else: 
            name = found['username']
        j.update({'keyword' : user, 'location' : loc, 'username' : [name]})
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

@app.route('/loggedin')
def loggedin():
	return 'yay'

@app.route('/', methods=['POST', 'GET'])
def index():
    if 'username' in session:
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
        found = dbUser.find_one({'keyword' : user, 'location' : loc})
        if found:
            if 'username' in found:
                if 'username' in session and not(session['username'] in found['username']):
                    found['username'].append(session['username'])
                elif(not('guest' in found['username']) and not('username' in session)):
                    found['username'].append('guest')
            else:
                name = ''
                if not('username' in session):
                    name = 'guest'
                else: 
                    name = found['username']
                found.update({'username' : [name]})
            jobs = found['jobs']
            print('cache') #Indicates that this has been search before and it is found in the db:
            
        else:
            body = '{ "keywords": "' + user + '", "location": "' + loc + '"}'
            connection.request('POST','/api/' + key, body, headers)
            response = connection.getresponse()
            j = response.read()
            j = json.loads(j)
            name = ''
            if not('username' in session):
                name = 'guest'
            else: 
                name = found['username']
            j.update({'keyword' : user, 'location' : loc, 'username' : [name]})
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

    return render_template('index.html')

@app.route('/logout')
def logout():
	session.clear()
	print(session)
	return 'You are logged out!'

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/login2')
def login2():
    return linkedin.authorize(callback=url_for('authorized', _external=True))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('login2'))
        
        return 'That username already exists!'

    return render_template('register.html')

@app.route('/login/authorized')
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    me = linkedin.get('people/~')
    #append data to mongodb
    return redirect(url_for('index'))


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug = True)
