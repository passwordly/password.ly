import json
import time

from passwordly import checkHash

class UserPassword:
  def __init__(self, db, username, hash):
    self.db = db
    self.username = username
    self.hash = hash

    self.key = 'sites-%s' % (self.hash)

  def setSite(self, site, comment=''):
    
    details = self.db.hget(self.key, site)

    if details:
      details = json.loads(details)
    else:
      details = {"created": time.time()}

    details["updated"] = time.time()

    # If the comment changed, keep a detailed history of it
    if "comment" in details and details["comment"] != comment:
      if not "comment-history" in details:
        details["comment-history"] = []

      details["comment-history"].append(details["comment"])

    # Ensure the comment is always saved
    details["comment"] = comment

    # Update the key in the database
    self.db.hset(self.key, site, json.dumps(details))

  def getDetails(self, site):
    details = self.db.hget(self.key, site)
    if details:
      return json.loads(details)
    else: return None

  def getComment(self, site):
    details = self.getDetails(site)

    if details and 'comment' in details:
      return details['comment']

    return None

  def getSites(self):
    return self.db.hkeys(self.key)

  def getAllComments(self):
    results = {}

    for site, value in self.db.hgetall(self.key).items():
      results[site] = json.loads(value)['comment']

    return results

  @staticmethod
  def fetch(db, username, password):
    'Convenience method to fetch a UserPassword object'
    user = User.fetch(db, username)
    if user:
      return user.getPassword(password)
    else:
      return None

class User:

  def __init__(self, db, username):
    self.db = db
    self.username = username

  def getPassword(self, password):
    passwords = self.db.lrange('passwords-%s' % self.username, 0, -1)
    for index in range(len(passwords)):
      if checkHash(password=password, hash=passwords[index]):
        return UserPassword(self.db, self.username, passwords[index])
    return None

  def addPasswordHash(self, hash):
    # Add the password to the list
    length = self.db.rpush('passwords-%s' % self.username, hash)

    # Return the index (length - 1)
    return UserPassword(self.db, self.username, hash)

  def getSites(self, password):
    password = self.getPassword(password)

    if not password:
      return None
    else:
      return password.getSites()

  @staticmethod
  def fetch(db, username):
    if not db.sismember('users', username):
      return None

    return User(db, username)

  @staticmethod
  def signup(db, username):
    # First double check the user doesn't exist
    if User.fetch(db, username):
      raise Exception('User already exists')

    # Fetch the user details from the signup
    details = json.loads(db.hget('signups', username))

    db.sadd('users', username)
    db.hset('user-created', username, time.time())

    user = User(db, username)

    password = user.addPasswordHash(details['hash'])

    password.setSite(details['site'])

    return user
