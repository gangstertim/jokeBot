#!/usr/bin/python

'''

Usage: jokebot.py [--debug] [-p <port>] [-H <host>]

Options:
  -p, --port=<port>    The port number on which to run Flask [default: 5000]
  -H, --host=<host>    The host to listen to [default: 127.0.0.1]
  --debug              Flag to determine debug mode [default: False]

'''

import json, requests, re, uuid
from collections import defaultdict
from flask import Flask, request, render_template
from docopt import docopt
from schema import Use, Schema
from random import choice, getrandbits, uniform
from redis import StrictRedis

app = Flask(__name__)

db = StrictRedis("localhost", 6379)
slack_url = "https://50onred.slack.com/services/hooks/incoming-webhook?token=YTQ9gokaGwwPe3nd8LSI1cv0"
def payload(text): return {"channel": "#jokestest", "username": "JokeBot", "text": text, "icon_emoji": ":ghost:"}
rimshot = {"channel": "#jokestest", "username": "RimshotBot", "text": "Ba-dum Tsh!", "icon_emoji": ":rimshot:"}
theJoke = {"channel": "#jokestest", "username": "ThatsTheJokeBot", "text": "That's the joke!!!", "icon_emoji": ":sweep:"}
COUNT = 50*10**6
help_message = "*Hi!  I'm Jokebot!*  To hear a joke, just say my name.  I'll also pipe in if I know jokes about the things you're talking about. If you'd like to tell me a joke, I'll add it to my collection: just say `jokebot, add this joke about TAG1, TAG2, TAG3: JOKE`.  You may add as many tags as you like!  Bye now! HOOOHOOHEEE HEE HAA HAAA lololololololololol"


laughs = ["AHAHAHAHHAHAHAHAHAHAAA",
          "ROFLCOPTAH   <--jokebot is from Boston",
          "OOOHEEE HAAAA HAAA HEEE HEE HOO",
          "tee hee hee",
          "Literally rolling on the floor laughing.  Literally.",
          "guffaw guffaw",
          "*chortle chortle*",
          "HAHAHAHAH",
          "They should call me Mr. Funny because that was GREAT!",
          "lol, good one, amirite? >__< :D",
          "Oh ho ho ho ho!",
          "*emits filthy snicker*",
          "lollersk8zz brooo",
          "lololololololololol",
          "hahahahahahha"]

messages = ["I've got a real knee-slapper for you!",
            "You're in luck, I've got just the thing.",
            "Here's a good one:",
            "I read this one on a candy wrapper!",
            "You better get your suture kit, because this one is so funny you'll be in stitches!",
            "Here's one of my favorites:",
            "I heard this one at the bar last night:",
            "My grandfather used to tell this one all the time.  It was so embarassing!",
            "My wife always slaps me when I say this one:",
            "Try this bad-boy on for size:"]

restricted_users = frozenset(["jshaak"])

with open('blacklist.txt') as f:
    blacklist = frozenset(f.read().split('\n'))

key_store = defaultdict(list)
joke_keys = db.keys("jokes:*")
for j in joke_keys:
    joke = json.loads(db.get(j))
    joke['count'] = COUNT
    key_store['*'].append(joke)
    for tag in joke['tags']:
        key_store[tag].append(joke)

@app.route('/', methods=['POST'])
def hello_world():
    orig   = request.form['text']
    string = request.form['text'].lower()
    user   = request.form['user_name']
    if string.strip(".!?(:)") == "i don't get it" or string == "i dont get it":
        return post_otherbot("theJoke")
    if user.lower() == "slackbot" and string != "ba-dum tsh!":
        if not bool(getrandbits(2)):  #1 in 3 chance of rimshot
            return post_otherbot("rimshot")
    elif user.lower() != "slackbot":
        word_array = [w.strip("!#$%&()*,-.:;?@^`~<>") for w in string.split(" ")]

        for w in word_array:
            if w == "jokebot":
                if re.search(r'add this \w+ about', string):
                    return add_joke(orig, user)
                for w in word_array:
                    if re.search(r"hel+p+", w):
                        return post_message(help_message)
                return post_message(add_laugh("Did somebody ask for a joke? %s  %s" % (choice(messages), choose_joke('*', key_store['*']))))
            elif w in key_store:
                return post_message(add_laugh("Did somebody say *%s*? Here's a joke about it! %s" % (w, choose_joke(w, key_store[w]))))
    return ""

def add_laugh(joke):
    if bool(getrandbits(1)): # Add laugh
        joke += "\n%s" % choice(laughs)
    return joke

def post_message(message):
    return json.dumps(payload(message))

def post_otherbot(type):
    if type == "rimshot":
        return json.dumps(rimshot)
    if type == "theJoke":
        return json.dumps(theJoke)

def choose_joke(tag, list_of_jokes):
    total = sum(i['count'] for i in list_of_jokes)
    r = uniform(0, total)
    upto = 0
    for joke in list_of_jokes:
        upto += joke['count']
        if upto >= r:
            joke['count'] /= 1.653      #scientifically proven to be the funniest ratio
            joke['log_data'][tag] += 1
            db.set(joke['id'], json.dumps(joke))
            return joke['joke']

    print "holy shit something smells of cabbage"

def add_joke(jokeString, user):
    if user.lower() in restricted_users:
        return post_message("Sorry, %s, but I don't like your jokes." % user)
    text      = re.search(r"about(.*?):(.*)", jokeString, flags=(re.S | re.I))
    joketext  = text.group(2)
    tags      = set([s.strip().lower() for s in re.split(r"\s*,\s*", text.group(1))])
    tags_good = set([s for s in tags if s.isalpha()
                       and len(s) >= 3
                       and s not in blacklist])
    tags_bad = tags - tags_good
    if tags_good:
        ident = "jokes:%s" % str(uuid.uuid4())
        joke = {
            'id': ident,
            'joke': joketext,
            'tags': list(tags_good),
            'count': COUNT,
            'log_data': dict([(t, 0) for t in tags_good] + [('*', 0)])
        }
        db.set(ident, json.dumps(joke))
        for tag in joke['tags']:
            if tag not in key_store:
                key_store[tag] = []
            key_store[tag].append(joke)
        key_store['*'].append(joke)
        if tags_bad:
            return post_message("Joke added successfully!  The following tags were ignored: %s" % ", ".join(tags_bad))
        else:
            return post_message("Joke added successfully!  that was sooooooooooo funnnnnnyyyyyyy")
    return post_message("you dun goofed bro")


@app.route('/plotdata', methods=['GET', 'POST'])
def plot():
    return render_template('plotBot/plot.html')

if __name__ == '__main__':
    args = Schema({'--host': Use(str), '--port': Use(int), '--debug': Use(bool)}).validate(docopt(__doc__))
    app.run(host=args['--host'], port=args['--port'], debug=args['--debug'])
