#!/usr/bin/env python
import re
import json
import uuid

from flask import request, render_template, redirect

import requests
import redis

import config

from user import User, UserPassword
from passwordly import generatePassword, createHash, checkHash
from util import app, db, log_event, get_distinct_id, set_distinct_id

# Import the routes for public/private area
import public
import private

@app.context_processor
def inject_debug():
  return dict(debug=config.debug)

@app.before_request
def before_request():
  # Redirect to SSL
  if config.ssl and request.headers.get('X-Forwarded-Proto', None) == 'http':
    url = config.base_url + request.path
    return redirect(url, 301)

  # Ensure we have a unique id
  if 'id' in request.cookies:
    distinct_id = request.cookies['id']
  else:
    distinct_id = uuid.uuid4().hex

  set_distinct_id(distinct_id)

  # Log a pageview
  log_event('pageview')


@app.after_request
def add_distinct_cookie(response):
  response.set_cookie('id', get_distinct_id(), 
      max_age=config.cookie_age,
      secure=config.ssl,
      httponly=True
    )
  return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('public/404.htm'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('public/500.htm'), 500

@app.route('/test/exception')
def test_exception():
  raise Exception('oops')

@app.route('/test/event')
def test_event():
  log_event('test', {'a': 1, 'c': 3, 'e': 'eee'})
  return 'Event logged.'

if __name__ == '__main__':
  app.debug = config.debug
  app.run()
