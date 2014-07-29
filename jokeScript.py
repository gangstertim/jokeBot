#!/usr/bin/python
import  json
from redis import StrictRedis


db = StrictRedis("localhost", 6379)

with open("data.json", "r") as jd:
    joke_list = json.load(jd)

i = 0

for joke in joke_list:
    db.set("jokes:%d" % i, json.dumps(joke))
    i += 1

db.set("counter", i)



