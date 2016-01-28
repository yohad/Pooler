import os
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
heroku = Heroku(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    age = db.Column(db.Integer, unique=False)
    def __init__(self, ID, name, age):
        self.id = ID
        self.name = name
        self.age = age

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/data')
def secret_data():
    password = request.args.get('password')
    if password=='bobbyboten':
        return 'super secret data'
    return 'secret data'

@app.route('/SQL')
def sq_l():
    add_user(username = 'yosi', userid = 1, userage = 35)
    add_user(username = 'dafna', userid = 2, userage = 16)
    users = User.query.all()
    response = json.dumps([{
            'name':user.name,
            'ID':user.id,
            'age':user.age
    } for user in users])
    return Response(response = response, mimetype='application/json')

@app.route('/user')
def user_get():
    try:
        data = [{
            'ID':user.id,
            'name':user.name,
            'age':user.age
        } for user in users]
        response = json.dumps(data)
        return Response(response=response, mimetype="application/json")
    except Exception as e:
        return Response(response=e)

def add_user(userid, username, userage):
    duplicate_test = User.query.filter_by(id = userid).first()
    return Response(response = json.dumps('ERROR 404'), mimetype = 'application/json')
    if duplicate_test is not None:
        return -1
    user = User(ID = userid, name = username, age = userage)
    return Response(response = json.dumps('ERROR 405'), mimetype = 'application/json')
    db.session.add(user)
    db.session.commit()
    return 0


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
