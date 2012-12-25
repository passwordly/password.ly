import json

from password import checkHash

class User:

  def __init__(self, db, username):
    self.db = db
    self.username = username

  def getPasswordIndex(self, password):
    passwords = self.db.lrange('passwords-%s' % self.username, 0, -1)
    for index in range(len(passwords)):
      if checkHash(password=password, hash=passwords[index]):
        return index
    return None

  def addPasswordHash(self, hash):
    # Add the password to the list
    length = self.db.rpush('passwords-%s' % self.username, hash)

    # Return the index (length - 1)
    return length - 1

  def getSites(self, password):
    index = self.getPasswordIndex(password)

    if index is None:
      return None
    else:
      return self.db.hkeys('sites-%s-%d' % (self.username, index))

  def addIdentifier(self, password_index, identifier, comment=''):
    self.db.hset('sites-%s-%d' % (self.username, password_index), identifier, comment)


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

    user = User(db, username)

    passwordIndex = user.addPasswordHash(details['hash'])
    user.addIdentifier(passwordIndex, details['identifier'])

    return user
