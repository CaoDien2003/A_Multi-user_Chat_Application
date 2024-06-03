from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import asyncio
import websockets
import json
from src.UsersAuthentication.database import MongoDB

app = Flask(__name__)
CORS(app)
db = MongoDB('mongodb://localhost:27017/')

# WebSocket server URL
WS_SERVER_URL = 'ws://localhost:6789'

async def send_token_to_ws_server(token):
    try:
        async with websockets.connect(WS_SERVER_URL) as websocket:
            await websocket.send(json.dumps({'action': 'authenticate', 'token': token}))
            response = await websocket.recv()
            return json.loads(response)
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")
        return None

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

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    user = db.get_by_phone(phone)
    if user and user['password'] == password:
        token = secrets.token_hex(16)
        db.add_token(phone, token)
        # Send token to WebSocket server
        ws_response = asyncio.run(send_token_to_ws_server(token))
        if ws_response and ws_response.get('message') == 'Authentication successful':
            return jsonify({'token': token, 'user': user}), 200
        else:
            return jsonify({'message': 'WebSocket authentication failed'}), 500
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
def get_all_users():
    users = db.get_all_users()
    return jsonify(users), 200

@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '')
    users = db.users_collection.find({"$or": [{"name": {"$regex": query, "$options": "i"}}, {"phone": {"$regex": query, "$options": "i"}}]})
    users_list = [{"name": user["name"], "phone": user["phone"], "_id": str(user["_id"])} for user in users]
    return jsonify(users_list), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
