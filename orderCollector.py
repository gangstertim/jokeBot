#!/usr/bin/python

'''

Usage: orderCollector.py [--debug] [-p <port>] [-H <host>]

Options:
  -p, --port=<port>    The port number on which to run Flask [default: 5000]
  -H, --host=<host>    The host to listen to [default: 127.0.0.1]
  --debug              Flag to determine debug mode [default: False]

'''

import json, requests, re, uuid
from flask import Flask, request
from docopt import docopt
from schema import Use, Schema

app = Flask(__name__)

slack_url = "https://50onred.slack.com/services/hooks/incoming-webhook?token=YTQ9gokaGwwPe3nd8LSI1cv0"
def payload(text): return {"channel": "#jokestest", "username": "JokeBot", "text": text, "icon_emoji": ":ghost:"}

@app.route('/', methods=['POST'])
def hello_world():
    orig   = request.form['text']
    string = request.form['text'].lower()
    user   = request.form['user_name']


    return post_message(("Did somebody say *%s*? Here's a joke about it! %s" % (w, choose_joke(key_store[w]))))

def post_message(message):
    return json.dumps(payload(message))

if __name__ == '__main__':
    args = Schema({'--host': Use(str), '--port': Use(int), '--debug': Use(bool)}).validate(docopt(__doc__))
    app.run(host=args['--host'], port=args['--port'], debug=args['--debug'])
