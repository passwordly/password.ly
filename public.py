import re
import json

from flask import request, render_template, redirect
from werkzeug.datastructures import ImmutableOrderedMultiDict
import requests

from user import User, UserPassword
from passwordly import generatePassword, createHash
from util import db, app, log_event

import config

@app.route('/', methods=['GET'])
def landing(name=None):
  return render_template('public/index.htm', name=name)

@app.route('/', methods=['POST'])
def public_post(name=None):

  password = str(request.form['password'])
  site = str(request.form['site'])
  
  result = generatePassword(password, site)
  params = {
    'password': password,
    'hash': createHash(password),
    'site': site,
    'result': result
  }

  log_event('public-generate')
  return render_template('public/password.htm', **params)

@app.route('/signup', methods=['POST'])
def signup():
  hash = str(request.form['hash'])
  site = str(request.form['site'])
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
      'site': site,
      'new_username': username,
      'error': error
    }
    return render_template('public/password.htm', **params)
  else:
    db.hset('signups', username, json.dumps({
        'hash': hash,
        'site': site
      }))

    log_event('request-signup', {
      'username': username
      })

    return redirect((config.paypal_url + '?cmd=_xclick' + \
        '&item_name=Signup+for+password.ly:+{username}' + \
        '&item_number={username}&amount={price}&business={email}' + \
        '&custom={username}' + \
        '&currency_code=USD' + \
        '&notify_url={ipn}' + \
        '&cancel_return=http://password.ly/paypal/cancel' + \
        '&return=http://password.ly/{username}').format(
          username=username,
          email=config.paypal_email,
          price=config.price,
          ipn=config.ipn_url
        ))

@app.route('/ipn',methods=['POST'])
def ipn():
  request.parameter_storage_class = ImmutableOrderedMultiDict

  # Store any/all ipn requests for future
  db.rpush('ipn', json.dumps(request.form))
  log_event('ipn', request.form)

  # Fetch details from request
  username = str(request.form['item_number'])

  # Double check all the details are correct
  if request.form['receiver_email'] != config.paypal_email:
    return 'Payment was not sent to correct email address'
  elif request.form['payment_status'] != 'Completed':
    return 'Payment status was not completed'
  elif request.form['mc_currency'] != 'USD':
    return 'Payment was not in USD'
  elif request.form['mc_gross'] != ('%.2f' % config.price):
    return 'Payment was not for the correct amount'


  # Validate that the actual request is correct
  validate_url = config.paypal_url + '?cmd=_notify-validate'

  values = request.form
  for x, y in values.iteritems():
    validate_url += "&{x}={y}".format(x=x,y=y)

  print 'Validating IPN using {url}'.format(url=validate_url)

  result = requests.get(validate_url)

  if result.text == 'VERIFIED':
    print "PayPal transaction was verified successfully."

    # Everything okay, actually perform the signup
    log_event('signup-complete', {"username": username})
    User.signup(db, username)
  else:
    print 'Paypal IPN string did not validate'

  return result.text
