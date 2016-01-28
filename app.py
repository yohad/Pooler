import os
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
heroku = Heroku(app)
db = SQLAlchemy(app)
user = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    age = db.Column(db.Integer, unique=False)
    def __init__(self, ID, name, age):
        self.id = ID
        self.name = name
        self.age = age

class Route(db.Model):
    start_lat = db.Column(db.Float, unique=False)
    start_lng = db.Column(db.Float, unique=False)
    destination_lat = db.Column(db.Float,unique=False)
    destination_lng = db.Column(db.Float, unique=False)
    driver_id = db.Column(db.Integer, primary_key=True)
    def __init__(self,st_lat,st_lng,dest_lat,dest_lng, id):
        self.start_lat = st_lat
        self.start_lng = st_lng
        self.destination_lat = dest_lat
        self.destination_lng = dest_lng
        self.driver_id = id

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
    ID = request.args.get('ID')
    users = User.query.all()
    response = json.dumps([{
            'name':user.name,
            'ID':user.id,
            'age':user.age
    } for user in users])
    return Response(response = response, mimetype='application/json')

@app.route('/signup/', methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        ID = request.args.get('id')
        name = request.args.get('name')
        age = request.args.get('age')
        if add_user(ID, name, age):
            return Response(response=json.dumps('Signup Successful'), mimetype='application/json')
        return Response(response=json.dumps('Signup Failed'), mimetype='application/json')

@app.route('/user')
def user_get():
    users = User.query.all()
    response = json.dumps([{
        'id':current_user.id,
        'name':current_user.name,
        'age':current_user.age
        } for current_user in users])
    return Response(response = response, mimetype = 'application/json')

@app.route('/travels/<int:id>', methods = ['GET'])
def get_travels(id):
    pass

def add_user(userid, username, userage):
    duplicate_test = User.query.filter_by(id = userid).first()
    if duplicate_test is not None:
        return False
    user = User(ID = userid, name = username, age = userage)
    db.session.add(user)
    db.session.commit()
    return True


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
