import os
from flask import Flask
from flask.ext.heroku import Heroku

app = Flask(__name__)
heroku = Heroku(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
