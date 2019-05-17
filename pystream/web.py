# code = uft-8

import pystream_class
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.debug = True
url = 'http://jbp.qrjdfh.cn/'
token = None
ps = pystream_class.Box(url, token=token)
ch = {}


@app.route('/')
def index():
    global ch
    channels = ps.channel()
    for t in channels:
        ch[t['title']] = t['name']
    return render_template('index.html', channel=channels)


@app.route('/<channel_title>')
def stream_lists(channel_title):
    stream_list = ps.list(ch[channel_title])
    if stream_list:
        return render_template('channel.html', stream_list=stream_list)
    else:
        return render_template('404.html')


if __name__ == '__main__':
    app.run()
