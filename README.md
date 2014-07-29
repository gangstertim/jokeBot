jokeBot
=======

jokeBot is a slack integration, built with Python + flask

Hook jokeBot up to an outgoing webhook to get him working!

Just type jokeBot help in the channel jokeBot is listening to and he'll tell you the format for adding new jokes.  data.json contains some jokes to get you started.

There are currently two verisons of jokeBot: jokeBot, which uses a .txt file to store JSON, and jokeBot2.0, which uses a redis store for jokes.  jokeBot2.0 is the only version being actively developed.
