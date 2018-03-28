import config

from flask import Flask, redirect, url_for, request
app = Flask(__name__)

import http.client
import json

@app.route('/success/<name>')
def success(name):
    return 'Jobs: %s' % name

@app.route('/login',methods = ['POST', 'GET'])
def login():
    host = 'us.jooble.org'
    key = config.apiKey()

    connection = http.client.HTTPConnection(host)
    #request headers
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    if request.method == 'POST':
        user = request.form['nm']
        loc = request.form['nn']
    else:
        user = request.args.get('nm')
        loc = request.form['nn']
    body = '{ "keywords": "' + user + '", "location": "' + loc + '"}'
    connection.request('POST','/api/' + key, body, headers)
    response = connection.getresponse()
    j = response.read()
    j = json.loads(j)
    jobs = j['jobs']
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

if __name__ == '__main__':
    app.run(debug = True)
