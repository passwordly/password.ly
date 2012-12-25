#!/usr/bin/env python
from flask import Flask, request, render_template
from password import generatePassword, createHash, checkHash
import json

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=1)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def landing(name=None):
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

def getUserPasswordIndex(username, password):
  passwords = r.lrange('passwords-%s' % username, 0, -1)
  for index in range(len(passwords)):
    if checkHash(password=password, hash=passwords[index]):
      return index
  return None

@app.route('/user/get-sites', methods=['POST'])
def user_get_sites():
  username = str(request.form['username'])
  password = str(request.form['password'])

  index = getUserPasswordIndex(username, password)

  if index is None:
    return '{"result": false, "sites": []}'
  else:
    sites = r.hkeys('sites-%s-%d' % (username, index))
    return json.dumps({"result": True, "sites": sites})

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
  
  params = {
    'username': username,
    'password': password,
    'identifier': identifier,
  }

  index = getUserPasswordIndex(username, password)
  if index is None:
    return render_template('private/unknown.htm', **params)
    
  params['comment'] = r.hget('sites-%s-%d' % (username, index), identifier)
  params['result'] = generatePassword(password, identifier)

  return render_template('private/password.htm', **params)

@app.route('/github-webhook')
def github_hook():
  os.system('git pull origin master')
  pass

if __name__ == '__main__':
  app.debug = True
  app.run()
