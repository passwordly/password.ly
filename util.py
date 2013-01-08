import time
import json

from redis import StrictRedis
from flask import Flask, request

import config

db = StrictRedis(host='localhost', port=6379, db=config.database)

app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'

# Allow keeping track of a per-request distinct_id
distinct_id = [None]

def get_distinct_id():
  return distinct_id[0]
def set_distinct_id(value):
  distinct_id[0] = value

# Log events
def log_event(event, properties={}):
  if 'X-Real-IP' in request.headers:
    remote_addr = str(request.headers['X-Real-IP'])
  else:
    remote_addr = request.remote_addr

  db.rpush('events', json.dumps({
        'event': event,
        'distinct_id': get_distinct_id(),
        'timestamp': time.time(),
        'remote_addr': remote_addr, 
        'platform': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'language': request.user_agent.language,
        'path': request.path,
        'url': request.url,
        'referrer': request.referrer, 
        'method': request.method, 
        'properties': properties
      }))


