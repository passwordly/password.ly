#!/usr/bin/env python
import re
import json

from flask import request, render_template, redirect
from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests
import redis

import config

from user import User, UserPassword
from passwordly import generatePassword, createHash, checkHash
from util import app, db

# Import the routes for public/private area
import public
import private

@app.context_processor
def inject_debug():
  return dict(debug=config.debug)

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
