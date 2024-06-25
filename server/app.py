#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == "GET":
        campers = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
        return campers, 200
    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )

            db.session.add(new_camper)
            db.session.commit()

            return new_camper.to_dict(), 200
        except ValueError:
            return {"errors": "Validation error"}, 400

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter_by(id=id).first()
    if camper:
        if request.method == 'GET':
            return camper.to_dict(), 200
        elif request.method == 'PATCH':
            data = request.get_json()
            try:
                for attr in data:
                    setattr(camper, attr, data[attr])

                db.session.commit()

                return camper.to_dict(), 202
            except ValueError:
                return {"errors": ["validation errors"]}, 400
    else:
        return {"error": "Camper not found"}, 404

@app.route('/activities', methods=['GET'])
def activities():
    activities = [activity.to_dict() for activity in Activity.query.all()]
    return activities, 200

@app.route('/activities/<int:id>', methods=['DELETE'])
def activities_by_id(id):
    activity = Activity.query.filter_by(id=id).first()
    if activity:
        db.session.delete(activity)
        return {}, 204
    else:
        return {"error": "Activity not found"}, 404
    
@app.route('/signups', methods=['POST'])
def signups():
    data = request.get_json()
    try:
        new_signup = Signup(
            time = data['time'],
            camper_id = data['camper_id'],
            activity_id = data['activity_id']        
        )
        db.session.add(new_signup)
        db.session.commit()

        return new_signup.to_dict(), 200
    except ValueError:
        return {"errors": ["validation errors"]}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)
