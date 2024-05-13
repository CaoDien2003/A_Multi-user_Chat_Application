from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity, jwt_required, unset_access_cookies, create_access_token, unset_jwt_cookies
from src.UsersAuthentication.database import MongoDB
import secrets

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

            token = secrets.token_hex(100)
            user_info = db.get_by_phone(phone)
            user_info['_id'] = str(user_info['_id'])
            db.add_token(phone,token)

            response_data = {'token': token, 'user_info': user_info, 'redirect_url': f'/signin/{phone}'}
            return response_data

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
        return jsonify(new_user), 201

@app.route('/signout', methods=['POST'])
@jwt_required()
def signout():
    try:
        # get token from request header or cookies
        token = request.headers.get('Authorization')
        if not token:
            return 'cannot get token', 400

        # Tìm user_id dựa vào token
        user = db.users_collection.find_one({'token': token})
        if user:
            db.users_collection.update_one(
                {'_id': user['_id']},
                {'$unset': {'token': ''}}
            )
            return 'signout success', 200
        else:
            return 'Token wrong', 401
    except Exception as e:
        return 'error:' + str(e), 500
