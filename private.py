import json

from flask import request, render_template, redirect

from user import User, UserPassword
from passwordly import generatePassword, createHash

from util import db, app, log_event

@app.route('/<string:username>/sync', methods=['POST'])
def user_sync(username):
  password = str(request.form['password'])

  user = User.fetch(db, username)
  user_password = user.getPassword(password)

  if not user_password:
    log_event('sync-fail', {'username': username})

    return '{"result": false, "sites": {}}'

  # Sync theirs into ours (where we don't have anything)
  theirs = json.loads(request.form['sites'])
  ours = user_password.getAllComments()

  for site, comment in theirs.items():
    if not site in ours:
      user_password.setSite(site, comment)
      ours[site] = comment

  log_event('sync', {'username': username})
  return json.dumps({"result": True, "sites": ours})

@app.route('/<string:username>/get-sites', methods=['POST'])
def user_get_sites(username):
  password = str(request.form['password'])

  user = User.fetch(db, username)

  sites = user and user.getSites(password)

  log_event('get-sites', {
    'username': username,
    'found': (sites is not None)
    })

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
  site = str(request.form['site'])
  
  params = {
    'username': username,
    'password': password,
    'site': site,
  }

  user_password = UserPassword.fetch(db, username, password)

  if not user_password:
    log_event('password-unknown', {
      'username': username,
      })
    return render_template('private/unknown.htm', **params)
    
  comment = user_password.getComment(site)
  if comment is not None:
    params['comment'] = comment

  params['result'] = generatePassword(password, site)

  log_event('user-generate', {
    'username': username,
    'new': (comment is not None)
    })
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
    

  log_event('add-password', {
    'username': username,
    })

  user.addPasswordHash(createHash(password))

  params = {
      'username': username,
      'message': 'Your new password is now available.'
  }
  return render_template('private/index.htm', **params)

@app.route('/<string:username>/save-comment', methods=['POST'])
def save_comment(username):
  password = str(request.form['password'])
  site = str(request.form['site'])
  comment = str(request.form['comment'])
  
  params = {
    'username': username,
    'password': password,
    'site': site,
  }

  user_password = UserPassword.fetch(db, username, password)
  new = user_password.getComment(site) is None

  if new:
    params['message'] = 'Your new site was saved.'
  else:
    params['message'] = 'Your comment was saved.'

  user_password.setSite(site, comment)

  params['comment'] = user_password.getComment(site)
  params['result'] = generatePassword(password, site)

  log_event('save-comment', {
    'username': username,
    'new': new
    })

  return render_template('private/password.htm', **params)



