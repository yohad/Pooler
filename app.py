import os
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    age = db.Column(db.Integer, unique=False)
    def __init__(self, ID, name, age):
        self.id = ID
        self.name = name
        self.age = age

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
heroku = Heroku(app)
db = SQLAlchemy(app)

db.create_all()
db.session.commit()

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
    try:
        yosi = User(name = 'Yosi', ID = 1, age = 32)
        dafna = User(name = 'Dafna', ID = 2, age = 16)
        db.session.add(yosi)
        db.session.add(dafna)
        db.session.commit()
        users = User.query.all()
        response = json.dumps(users)
        return Response(response = response, mimetype='application/json')
    except Exception as e:
        return Response(response=e)

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
