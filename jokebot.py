#!/usr/bin/python

'''

Usage: jokebot.py [--debug] [-p <port>] [-H <host>]

Options:
  -p, --port=<port>    The port number on which to run Flask [default: 5000]
  -H, --host=<host>    The host to listen to [default: 127.0.0.1]
  --debug              Flag to determine debug mode [default: False]

'''

import atexit, json, requests, re
from flask import Flask, request
from docopt import docopt
from schema import Use, Schema
from random import choice, getrandbits, uniform

app = Flask(__name__)

jokeCount = 0
payload = {"channel": "#jokestest", "username": "JokeBot", "text": "", "icon_emoji": ":ghost:"}
rimshot = {"channel": "#jokestest", "username": "RimshotBot", "text": "Ba-dum Tsh!", "icon_emoji": ":rimshot:"}
theJoke = {"channel": "#jokestest", "username": "ThatsTheJokeBot", "text": "That's the joke!!!", "icon_emoji": ":sweep:"}
COUNT = 50*10**6
laughs = ["AHAHAHAHHAHAHAHAHAHAAA",
          "ROFLCOPTAH   <--jokebot is from Boston",
          "OOOHEEE HAAAA HAAA HEEE HEE HOO",
          "tee hee hee",
          "guffaw guffaw",
          "*chortle chortle*",
          "HAHAHAHAH",
          "lol, good one, amirite? >__< :D",
          "Oh ho ho ho ho!",
          "*emits filthy snicker*",
          "lololololololololol",
          "hahahahahahha"]

messages = ["I've got a real knee-slapper for you!",
	    "You're in luck, I've got just the thing.",
	    "Here's a good one:",
	    "Here's one of my favorites:",
	    "I heard this one at the bar last night:",
	    "My grandfather used to tell this one all the time.  It was so embarassing!",
	    "My wife always slaps me when I say this one:",
	    "Try this bad-boy on for size:"]
 
with open("data.json", "r") as jd:
    joke_list = json.load(jd)

key_store = {}
key_store['*'] = []
for joke in joke_list:
    joke['count'] = COUNT
    key_store['*'].append(joke)
    for tag in joke['tags']:
        if tag not in key_store:
            key_store[tag] = []
        key_store[tag].append(joke)
       
@app.route('/', methods=['POST'])
def hello_world():
    orig = request.form['text']
    string = request.form['text'].lower()
    user = request.form['user_name']
    if string.strip(".!?(:)") == "i don't get it" or string == "i dont get it":
	return post_otherbot("theJoke")
    if user.lower() == "slackbot" and string != "ba-dum tsh!":
	if not bool(getrandbits(2)):  #1 in 3 chance of rimshot
	    return post_otherbot("rimshot")
    elif user.lower() != "slackbot":
        word_array = [w.strip("!#$%&()*,-.:;?@^`~<>") for w in string.split(" ")]
        
        for w in word_array:
            if w == "jokebot":
                if "add this joke about" in string:
                    if user.lower() == "jshaak":
			return post_joke("Sorry, %s, but I don't like your jokes." % user)
		    elif add_joke(orig): return post_joke("Joke added successfully!  that was sooooooooooo funnnnnnyyyyyyy")
                    else: return post_joke("you dun goofed bro")

                for w in word_array:
                    if re.search(r"hel+p+", w):
                        return post_joke("""*Hi!  I'm Jokebot!*  To hear a joke, just say my name.  I'll also pipe in if I know jokes about the things you're talking about. If you'd like to tell me a joke, I'll add it to my collection: just say `jokebot, add this joke about TAG1, TAG2, TAG3: JOKE`.  You may add as many tags as you like!  Bye now! HOOOHOOHEEE HEE HAA HAAA lololololololololol""")

                return post_joke(add_message("Did somebody ask for a joke?"))
            elif w in key_store:
                return post_joke("Did somebady say *%s*? Here's a joke about it! %s" % (w, choose_joke(key_store[w])))
    return ""

def add_message(intro):
    intro += " %s  %s" % (choice(messages), choose_joke(key_store['*']))
    return intro

def post_joke(joke):
    payload['text'] = joke
    if bool(getrandbits(1)): # Add laugh
        payload['text'] += "\n%s" % choice(laughs)
    return json.dumps(payload)

def post_otherbot(type):
    if type == "rimshot":
        return json.dumps(rimshot)
    if type == "theJoke":
        return json.dumps(theJoke)

def choose_joke(list_of_jokes):
    total = sum(i['count'] for i in list_of_jokes)
    r = uniform(0, total)
    upto = 0
    for joke in list_of_jokes:
        upto += joke['count']
        if upto >= r:
            joke['count'] /= 1.653      #scientifically proven to be the funniest ratio
            return joke['joke']

    print "holy shit something smells of cabbage"

def add_joke(jokeString):
    tags = re.search(r"about(.*?):(.*)", jokeString, flags=(re.S | re.I))
    if tags: 
        joke = {'joke': tags.group(2), 'tags': [s.strip() for s in re.split(r"\s*,\s*", tags.group(1))], 'count': COUNT}
        for tag in joke['tags']:
            if tag not in key_store:
                key_store[tag] = []
            key_store[tag].append(joke)
        key_store['*'].append(joke)
        return True
    return False


@atexit.register
def save_jokes():
    ks = []
    for joke in key_store['*']:
        ks.append({'joke': joke['joke'], 'tags': joke['tags']})
    with open('data.json', 'w') as f:
        json.dump(ks, f, indent=4)

if __name__ == '__main__':
    args = Schema({'--host': Use(str), '--port': Use(int), '--debug': Use(bool)}).validate(docopt(__doc__))
    app.run(host=args['--host'], port=args['--port'], debug=args['--debug'])



