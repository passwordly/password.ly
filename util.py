from redis import StrictRedis
from flask import Flask

import config

db = StrictRedis(host='localhost', port=6379, db=config.database)

app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'

