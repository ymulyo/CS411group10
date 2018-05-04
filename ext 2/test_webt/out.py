import config

from flask import Flask, redirect, url_for, request, render_template, render_template, session, jsonify
from flask_pymongo import PyMongo
from flask_oauthlib.client import OAuth
from datetime import datetime

import bcrypt

'''Connects to mlab'''
app = Flask(__name__)
app.config['MONGO_DBNAME'] = config.dbName()
app.config['MONGO_URI'] = config.mongoURI()

oauth = OAuth(app)

mongo = PyMongo(app)



import http.client
import json

hashpass = ''

'''Linkedin oauth.
---With how Linkedin's limited free API, we were'nt able to extract the information
---we originally hoped for. Because of this, though the oauth work, we have to decided
---to not put it in for now. '''
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

'''Testing the main page that contains CSS for better appearance.
Somehow still can't exactly figure out the changes neede to succesfully have
CSS working with python's flask during run time. Therefore, this page is currently unused.
The goal was that this page would have had all the information and logout button. The information
would have been shown as pictures, company name, and titles corresponding to the job you search and where,
which is achieved by using JOOBLE's API. We've also hit another bump when trying to find a suitable API for
an image genrator since the database server we use, mlab, is limited to only 16mb which isn't many.'''

@app.route('/test/<name>')
def test(name):
   name = name.replace("'", "")
   name = name.replace("[", "")
   name = name.replace("]", "")
   array = name.split(',')
   user = {'link' : "https://www.google.com", 'company' : array[0], 'companytwo' : array[1], 'companythree' : array[2], 'companyfour' : array[3], 'companyfive' : array[4]}
  # user1 = {'link' : "https://www.google.com", 'company' : array[1]}
  # user2 = {'link' : "https://www.google.com", 'company' : array[2]}
  # user3 = {'link' : "https://www.google.com", 'company' : array[3]}
  # user4 = {'link' : "https://www.google.com", 'company' : array[4]}
  #userarray = [user, user1, user2, user3, user4]
   return render_template('myPage.html', user=user)

''' 
This function handles the search implementation we have on most of our search bars.
Before calling the API (and wasting the limited API calls we have), it checks our DB
to see if such call were made before. If so, then it would fetch the data received before hand
from the DB, else create a new API call. We also have connected keyword and location calls to
each user as our goal was to customize the mainpage according to the login user. What could be
optimized is to create a timestamp also as previously store data in the DB could easily be
outdated. The problem was finding the right time to know when something is outdated, as technically
the lower the threshold you set, the more likely your data is up-to-date but it also means more
frequent API calls.
 '''

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
        if 'username' in session:
            if not(session['username'] in found):
                found.update({session['username'] : 1})
        else:
            if not('guest' in found):
                found.update({'guest' : 1})
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
            name = session['username']
        j.update({'keyword' : user, 'location' : loc, name : 1})
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
    return redirect(url_for('test',name = user)) #redirect to search with boxes
    #return redirect(url_for('emails',name = user))
    #return render_template('results.html', email_addresses=user)

'''
@app.route('/loggedin')
def loggedin():
	return 'yay'
'''

'''
When opening the new tab with the extension in Chrome, you will be directed to a front page
where you can search for a job. After trying to search, if you aren't logged in, you will be redirected to a login
page where you can login using an existing account or you can create a new one. If you are already logged in, it will
automatically do a search for you and redirect you to the main page.
'''
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
            if 'username' in session:
                if not(session['username'] in found):
                    found.update({session['username'] : 1})
            else:
                if not('guest' in found):
                    found.update({'guest' : 1})
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
                name = session['username']
            j.update({'keyword' : user, 'location' : loc, name : 1})
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
        return redirect(url_for('success',name = user))#redirect to serach with boxes

    return render_template('index.html')

'''
Logout route that clears session.
'''

@app.route('/logout')
def logout():
	session.clear()
	print(session)
	return 'You are logged out!'

'''
Login route.
Check if such user with the right password exist.
'''

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

'''
Twitter oauth login
'''
@app.route('/login2')
def login2():
    return linkedin.authorize(callback=url_for('authorized', _external=True))

'''
For new users trying to register. Username and password will be stored in the DB.
Password is encrypted using bcrypt.
'''
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')

'''
Linkedin oauth
'''

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
    return redirect(url_for('index')) #mypagehtml

"""@app.route('/home')
def home():
    dbUser = mongo.db.users
    dbUser."""

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
