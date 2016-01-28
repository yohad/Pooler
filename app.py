import os
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text


app = Flask(__name__)
heroku = Heroku(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/data')
def secret_data():
    password = request.args.get('password')
    if password=='bobbyboten':
        return 'super secret data'
    return 'secret data'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
