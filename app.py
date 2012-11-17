#!/usr/bin/env python
from flask import Flask, request, render_template
from password import generatePassword

app = Flask(__name__)

@app.route('/')
def index(name=None):
  return render_template('index.html', name=name)
#return "<form action='/generate' method='post'><input type='password' name='password' /><input type='text' name='site' /><input type='submit' /></form>"

@app.route('/generate', methods=['POST'])
def generate():
  password = str(request.form['password'])
  site = str(request.form['site'])
  print password, site
  return generatePassword(password, site)

@app.route('/github-webhook')
def github_hook():
  pass

if __name__ == '__main__':
  app.debug = True
  app.run()
