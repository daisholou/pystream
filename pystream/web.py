# code = uft-8

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hi beauty!'


if __name__ == '__main__':
    app.run()
