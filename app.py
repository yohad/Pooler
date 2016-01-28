import os
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text

class User:
    def __init__(self, ID, name, age):
        self.id = ID
        self.name = name
        self.age = age

yosi = User(209929256, 'yosi', 25)
david = User(158627528, 'david', 34)
users = [yosi, david]

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

@app.route('/user')
def user_get():
    global users
    response = json.dumps([
    {
        'ID':user.id,
        'name':user.name,
        'age':user.age
    }
    ] for user in users)
    return Response(response=response, mimetype="application/json")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
