import os
import math
from flask import Flask, request, Response, json
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import text
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
heroku = Heroku(app)
db = SQLAlchemy(app)
user = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    age = db.Column(db.Integer, unique=False)
    sex = db.Column(db.String, unique=False)
    def __init__(self, ID, name, age, sex):
        self.id = ID
        self.name = name
        self.age = age
        self.sex=sex

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

@app.route('/id/')
def check_id():
    id = request.args.get('id')
    user = User.query.filter_by(id=id).first()
    if user is None:
        return Response(response=json.dumps('0'))
    return Response(response=json.dumps('1'))


@app.route('/signup/')
def signup():
    ID = request.args.get('id')
    name = request.args.get('name')
    age = request.args.get('age')
    #sex = request.args.get('sex')
    if add_user(ID, name, age):
        return Response(response=json.dumps('Signup Successful'), mimetype='application/json')
    return Response(response=json.dumps('Signup Failed'), mimetype='application/json')

@app.route('/users/')
def users_get():
    users = User.query.all()
    response = json.dumps([{
        'id':current_user.id,
        'name':current_user.name,
        'age':current_user.age,
        #'sex':current_user.sex
        } for current_user in users])
    return Response(response = response, mimetype = 'application/json')

@app.route('/user/')
def get_user():
    id = request.args.get('id')
    user = User.query.filter_by(id=id).first()
    return Response(response=json.dumps({
        'name':user.name,
        'age':user.age,
        #'sex':user.sex
    }))

@app.route('/findroutes/')
def find_routes():
    try:
        slat = request.args.get('slat')
        slng = request.args.get('slng')
        dlat = request.args.get('dlat')
        dlng = request.args.get('dlng')

        if None in [slat, slng, dlat, dlng]:
            return Response(response='Invalid arguments.')

        routes = find_matching_routes(slat,slng,dlat,dlng)
        return Response(response=json.dumps([{
            'driver_id':route[0].driver_id,
            'walking_distance':route[1]
        } for route in routes]), mimetype='application/json')
    except Exception as e:
        return Response(response=e)
@app.route('/travels/', methods = ['GET', 'POST'])
def get_travels():
    try:
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
                'destination_longtitude':route.destination_lng,
                'start':route.start,
                'destination':route.destination
            })
            return Response(response=resp, mimetype = 'application/json')
    except Exception as e:
        return Response(response=e)
@app.route('/routestart/')
def route_start():
    try:
        id = request.args.get('id')
        slat = request.args.get('slat')
        slng = request.args.get('slng')
        dlat = request.args.get('dlat')
        dlng = request.args.get('dlng')
        if not add_route(dlat, dlng, slat, slng, id):
            return Response(response=json.dumps('Route registration failed'))
        return Response(response=json.dumps('Route registration completed successfully'))
    except Exception as e:
        return Response(response=e)

@app.route('/endride/')
def end_ride():
    driver_id = request.args.get('id')
    Route.query.filter_by(driver_id=driver_id).delete()
    db.session.commit()
    return Response(response=json.dumps('1'))

@app.route('/gps/')
def update_location():
    id = request.args.get('id')
    lat = request.args.get('lat')
    lon = request.args.get('lng')
    route = Route.query.filter_by(driver_id=id).first()
    if route is None:
        return Response(response=json.dumps('No such route'))
    route.start_lat = lat
    route.start_lng = lon
    db.session.commit()

def add_user(userid, username, userage, sex = None):
    duplicate_test = User.query.filter_by(id = userid).first()
    if duplicate_test is not None:
        return False
    user = User(ID = userid, name = username, age = userage, sex = sex)
    db.session.add(user)
    db.session.commit()
    return True

def add_route(dlat,dlng,slat,slng,id):
    route_test = Route.query.filter_by(driver_id = id).first()
    if route_test is not None:
        return False
    route = Route(st_lat=slat,st_lng=slng,dest_lat=dlat,dest_lng=dlng,id=id)
    db.session.add(route)
    db.session.commit()
    return True


def find_matching_routes(slat,slng,dlat,dlng):
    routes = []
    all_routes = Route.query.all()
    routes_by_distance = []
    for route in all_routes:
        routes_by_distance.append((route, math.sqrt(math.pow(route.start_lat-slat,2)+math.pow(route.start_lng-slng,2))+\
                                    math.sqrt(math.pow(route.destination_lat-dlat,2)+math.pow(route.destination_lng-dlng,2))))
    routes_by_distance.sort(key = lambda x: x[1])
    for i in routes_by_distance[:5]:
        routes.append((i[0],i[1]/0.010239))
    return routes



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
