#!/usr/bin/env python
from flask import Flask, request, render_template
from password import generatePassword

app = Flask(__name__)

@app.route('/', methods=['GET'])
def landing(name=None):
  return 'l'
  return render_template('public/index.htm', name=name)

@app.route('/', methods=['POST'])
def public_post(name=None):
  password = str(request.form['password'])
  identifier = str(request.form['identifier'])
  
  result = generatePassword(password, identifier)
  params = {
    'password': password,
    'identifier': identifier,
    'result': result
  }
  return render_template('public/password.htm', **params)

@app.route('/<path:username>')
def user_landing(username):
  params = {
      'username': username
  }
  return render_template('private/index.htm', **params)

@app.route('/<path:username>', methods=['POST'])
def user_post(username):
  password = str(request.form['password'])
  identifier = str(request.form['identifier'])
  
  result = generatePassword(password, identifier)
  params = {
    'password': password,
    'identifier': identifier,
    'result': result
  }
  return render_template('private/password.htm', **params)

@app.route('/github-webhook')
def github_hook():
  pass

if __name__ == '__main__':
  app.debug = True
  app.run()
