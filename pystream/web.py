# code = uft-8

import pystream_class
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.debug = True

ps = pystream_class.Box()
ch = {}
stream_list = {}


@app.route('/')
def index():
    global ch
    channels = ps.channel()
    for t in channels:
        ch[t['title']] = {'name': t['title'], 'json': t['name']}
    return render_template('index.html', channel=channels)


@app.route('/<channel_title>')
def stream_lists(channel_title):
    global stream_list
    stream_list[channel_title] = ps.list(ch[channel_title])
    if stream_list:
        return render_template('channel.html', stream_list=stream_list)
    else:
        return render_template('404.html')


@app.route('/<channel_title>/<stream>')
def stream_play(channel_title, stream):
    player = stream_list[channel_title][stream]
    if player:
        return render_template('play.html', player=player)
    else:
        return render_template('404.html')


if __name__ == '__main__':
    app.run()
