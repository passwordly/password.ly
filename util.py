from redis import StrictRedis

import config

db = StrictRedis(host='localhost', port=6379, db=config.database)
