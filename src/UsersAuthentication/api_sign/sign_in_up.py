from flask import Flask, request, jsonify
from src.UsersAuthentication.database import MongoDB
from bson import json_util

app = Flask(__name__)
db = MongoDB('mongodb://localhost:27017/')

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    user = db.get_by_phone(phone)

    if user:
        if user['password'] == password:
            return jsonify({'message': 'Logged in successfully'})
        else:
            return jsonify({'message': 'wrong password'}), 401
    else:
        return jsonify({'message': 'Account has not been created'}), 404

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    password = data.get('password')

    existing_user = db.get_by_phone(phone)
    if existing_user:
        return jsonify({'message': 'Phone number already exists'}), 409
    else:
        new_user_id = db.add_user(name, phone, password)
        new_user = db.get_by_id(new_user_id)
        return json_util.dumps(new_user), 201

