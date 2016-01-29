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
    id = None
    def __init__(self,start,destination,st_lat,st_lng,dest_lat,dest_lng, id):
        self.start_lat = st_lat
        self.start_lng = st_lng
        self.destination_lat = dest_lat
        self.destination_lng = dest_lng
        self.driver_id = id

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

@app.route('/signup/')
def signup():
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

@app.route('/findroutes/')
def find_routes():
    slat = request.args.get('slat')
    slng = request.args.get('slng')
    dlat = request.args.get('dlat')
    dlng = request.args.get('dlng')

    if None in [slat, slng, dlat, dlng]:
        return Response(response='Invalid arguments.')

    routes = find_matching_routes(slat,slng,dlat,dlnt)
    return Response(response=json.dumps([route.id for route in routes]), mimetype='application/json')

@app.route('/travels/', methods = ['GET', 'POST'])
def get_travels():
    id = request.args.get('id')
    driver = User.query.filter_by(id = id).first()
    if driver is None:
        return Response(response = json.dumps('There is no such user in the database.'))
    if request.method == 'GET':
        route = Route.query.filter_by(driver_id = id).first()
        if route is None:
            return Response(response = json.dumps('There is no such route.'))
        resp = json.dumps({
            'start_latitude':route.start_lat,
            'start_longtitude':route.start_lng,
            'destination_latitude':route.destination_lat,
            'destination_longtitude':route.destination_lng
        })
        return Response(response=resp, mimetype = 'application/json')
    elif request.method == 'POST':
        try:
            slat = request.args.get('slat')
            slng = request.args.get('slng')
            dlat = request.args.get('dlat')
            dlng = request.args.get('dlng')
            start = request.args.get('start')
            destination = request.args.get('dest')
            if not add_route(dlat, dlng, slat, slng, id, start, destination):
                return Response(response=json.dumps('Route registration failed'))
            return Response(response=json.dumps('Route registration completed successfully'))
        except Exception as e:
            return Response(response=e)

def add_user(userid, username, userage):
    duplicate_test = User.query.filter_by(id = userid).first()
    if duplicate_test is not None:
        return False
    user = User(ID = userid, name = username, age = userage)
    db.session.add(user)
    db.session.commit()
    return True

def add_route(dlat,dlng,slat,slng,id,start,destination):
    route_test = Route.query.filter_by(id = id).first()
    if route_test is not None:
        return False
    route = Route(st_lat=slat,st_lng=slng,dest_lat=dlat,dest_lng=dlng,id=id, start = start, destination = destination)
    db.session.add(route)
    db.session.commit()
    return True

def find_matching_routes(slat,slng,dlat,dlng):
    routes = Route.query.filter_by(slat=slat).filter_by(slng=slng).filter_by(dlat=dlat).filter_by(dlng=dlng)
    return routes
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
