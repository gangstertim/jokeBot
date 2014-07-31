import json
from redis import StrictRedis

db = StrictRedis(host='localhost', port=6379)
jokes = [dict(json.loads(db.get(k))['log_data'].items() + [('jokeId', k)]) for k in db.keys('jokes:*')]
with open('jokedata.json', 'w') as f:
    json.dump(jokes, f, indent=2)
