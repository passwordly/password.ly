#!/usr/bin/env python
import re
import json

from flask import Flask, request, render_template, redirect
from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests
import redis

import config
from user import User
from password import generatePassword, createHash, checkHash

r = redis.StrictRedis(host='localhost', port=6379, db=config.database)
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
    'hash': createHash(password),
    'identifier': identifier,
    'result': result
  }
  return render_template('public/password.htm', **params)

@app.route('/signup', methods=['POST'])
def signup():
  hash = str(request.form['hash'])
  identifier = str(request.form['identifier'])
  username = str(request.form['username'])
  
  error = None

  if User.fetch(r, username):
    error = "The username you selected is taken."
  elif not re.match(r'^[a-z]+$', username):
    error = 'Your username can only be made of lowercase letters'
  elif username in config.reserved:
    error = 'Sorry, the username you have selected is reserved'

  if error:
    params = {
      'hash': hash,
      'identifier': identifier,
      'new_username': username,
      'error': error
    }
    return render_template('public/password.htm', **params)
  else:
    r.hset('signups', username, json.dumps({
        'hash': hash,
        'identifier': identifier
      }))

    return redirect((config.paypal_url + '?cmd=_xclick' + \
        '&item_name=Signup+for+password.ly:+{username}' + \
        '&item_number={username}&amount=15&business={email}' + \
        '&custom={username}' + \
        '&currency_code=USD' + \
        '&cancel_return=http://password.ly/paypal/cancl' + \
        '&return=http://password.ly/{username}').format(
          username=username, email=config.paypal_email
        ))

@app.route('/user/get-sites', methods=['POST'])
def user_get_sites():
  username = str(request.form['username'])
  password = str(request.form['password'])

  user = User.fetch(r, username)

  sites = user and user.getSites(password)

  if not sites:
    return '{"result": false, "sites": []}'
  else:
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

  user = User.fetch(r, username)
  index = user and user.getPasswordIndex(password)
  if index is None:
    return render_template('private/unknown.htm', **params)
    
  params['comment'] = r.hget('sites-%s-%d' % (username, index), identifier)
  params['result'] = generatePassword(password, identifier)

  return render_template('private/password.htm', **params)

@app.route('/ipn',methods=['POST'])
def ipn():
  request.parameter_storage_class = ImmutableOrderedMultiDict

  # Store any/all ipn requests for future
  r.rpush('ipn', json.dumps(requests.form))

  validate_url = config.paypal_url + '?cmd=_notify-validate'

  values = request.form
  for x, y in values.iteritems():
    validate_url += "&{x}={y}".format(x=x,y=y)

  print 'Validating IPN using {url}'.format(url=validate_url)

  r = requests.get(validate_url)

  if r.text == 'VERIFIED':
    print "PayPal transaction was verified successfully."
  else:
    print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

  return r.text

@app.route('/github-webhook')
def github_hook():
  os.system('git pull origin master')
  pass

@app.route('/test')
def test():
  print User.signup(r, 'qix')

if __name__ == '__main__':
  app.debug = True
  app.run()
