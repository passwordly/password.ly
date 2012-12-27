#!/usr/bin/env python
import re
import json

from flask import Flask, request, render_template, redirect
from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests
import redis

import config

from user import User, UserPassword
from passwordly import generatePassword, createHash, checkHash
from util import db

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

  if User.fetch(db, username):
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
    db.hset('signups', username, json.dumps({
        'hash': hash,
        'identifier': identifier
      }))

    return redirect((config.paypal_url + '?cmd=_xclick' + \
        '&item_name=Signup+for+password.ly:+{username}' + \
        '&item_number={username}&amount=15&business={email}' + \
        '&custom={username}' + \
        '&currency_code=USD' + \
        '&notify_url={ipn}' + \
        '&cancel_return=http://password.ly/paypal/cancel' + \
        '&return=http://password.ly/{username}').format(
          username=username,
          email=config.paypal_email,
          ipn=config.ipn_url
        ))

@app.route('/user/get-sites', methods=['POST'])
def user_get_sites():
  username = str(request.form['username'])
  password = str(request.form['password'])

  user = User.fetch(db, username)

  sites = user and user.getSites(password)

  if sites is None:
    return '{"result": false, "sites": []}'
  else:
    return json.dumps({"result": True, "sites": sites})

@app.route('/<string:username>')
def user_landing(username):
  params = {
      'username': username
  }
  return render_template('private/index.htm', **params)

@app.route('/<string:username>', methods=['POST'])
def user_post(username):
  password = str(request.form['password'])
  identifier = str(request.form['identifier'])
  
  params = {
    'username': username,
    'password': password,
    'identifier': identifier,
  }

  user_password = UserPassword.fetch(db, username, password)

  if not user_password:
    return render_template('private/unknown.htm', **params)
    
  comment = user_password.getComment(identifier)
  print comment is None, 'x'
  if comment is not None:
    params['comment'] = comment

  params['result'] = generatePassword(password, identifier)

  return render_template('private/password.htm', **params)

@app.route('/<string:username>/add-password', methods=['POST'])
def add_password(username):
  password = str(request.form['password'])
  confirm_password = str(request.form['confirm_password'])
  existing_password = str(request.form['existing_password'])
  
  params = {
    'username': username,
    'password': password,
  }

  user = User.fetch(db, username)

  error = None

  if not user.getPassword(existing_password):
    error = "The existing password you entered was not found."

  if error is None and password != confirm_password:
    error = "The password you entered to confirm was not the same as entered originally."

  if error:
    return render_template('private/unknown.htm', error=error, **params)
    
  user.addPasswordHash(createHash(password))

  params = {
      'username': username,
      'message': 'Your new password is now available.'
  }
  return render_template('private/index.htm', **params)

@app.route('/<string:username>/save-comment', methods=['POST'])
def save_comment(username):
  password = str(request.form['password'])
  identifier = str(request.form['identifier'])
  comment = str(request.form['comment'])
  
  params = {
    'username': username,
    'password': password,
    'identifier': identifier,
  }

  user_password = UserPassword.fetch(db, username, password)

  if user_password.getComment(identifier) is None:
    params['message'] = 'Your new site was saved.'
  else:
    params['message'] = 'Your comment was saved.'

  user_password.setIdentifier(identifier, comment)

  params['comment'] = user_password.getComment(identifier)
  params['result'] = generatePassword(password, identifier)

  return render_template('private/password.htm', **params)


@app.route('/ipn',methods=['POST'])
def ipn():
  request.parameter_storage_class = ImmutableOrderedMultiDict

  # Store any/all ipn requests for future
  db.rpush('ipn', json.dumps(requests.form))

  validate_url = config.paypal_url + '?cmd=_notify-validate'

  values = request.form
  for x, y in values.iteritems():
    validate_url += "&{x}={y}".format(x=x,y=y)

  print 'Validating IPN using {url}'.format(url=validate_url)

  result = requests.get(validate_url)

  if result.text == 'VERIFIED':
    print "PayPal transaction was verified successfully."
  else:
    print 'Paypal IPN string {arg} did not validate'.format(arg=arg)

  return result.text

@app.route('/github-webhook')
def github_hook():
  os.system('git pull origin master')
  pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('public/404.htm'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('public/500.htm'), 500

@app.route('/test/exception')
def test_exception():
  raise Exception('oops')

if __name__ == '__main__':
  app.debug = config.debug
  app.run()
