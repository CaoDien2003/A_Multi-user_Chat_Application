from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import asyncio
import websockets
import json
from src.UsersAuthentication.database import MongoDB

app = Flask(__name__)
CORS(app)  # Add this line to enable CORS for all routes

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

@app.route('/get_user_by_phone', methods=['GET'])
def get_user_by_phone():
    phone = request.args.get('phone')
    if not phone:
        return jsonify({'message': 'Phone number is required'}), 400

    user = db.get_by_phone(phone)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'name': user.get('name'), 'phone': user.get('phone')}), 200

@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '')
    users = db.users_collection.find({"$or": [{"name": {"$regex": query, "$options": "i"}}, {"phone": {"$regex": query, "$options": "i"}}]})
    users_list = [{"name": user["name"], "phone": user["phone"], "_id": str(user["_id"])} for user in users]
    return jsonify(users_list), 200

@app.route('/create_room', methods=['POST'])
def create_room():
    data = request.get_json()
    room_name = data.get('room_name')
    users = data.get('users')

    existing_room = db.get_room_by_name(room_name)
    if existing_room:
        return jsonify({'message': 'Room already exists'}), 409
    else:
        new_room_id = db.create_room(room_name, users)
        new_room = db.get_room_by_name(room_name)
        return jsonify(new_room), 201

@app.route('/search_rooms', methods=['GET'])
def search_rooms():
    query = request.args.get('query', '')
    token = request.args.get('token', '')

    user = db.get_by_token(token)
    if not user:
        return jsonify({'message': 'Invalid token'}), 401

    user_rooms = db.get_rooms_by_user(user['phone'])  # Assuming phone is the unique identifier
    matched_rooms = [room for room in user_rooms if 'name' in room and query.lower() in room['name'].lower()]

    return jsonify(matched_rooms), 200

@app.route('/get_room_users', methods=['GET'])
def get_room_users():
    room_name = request.args.get('room')
    if not room_name:
        return jsonify({'message': 'Room name is required'}), 400

    room = db.get_room_by_name(room_name)
    if not room:
        return jsonify({'message': 'Room not found'}), 404

    return jsonify({'users': room.get('users', [])}), 200

@app.route('/all_rooms', methods=['GET'])
def get_all_rooms():
    rooms = db.get_all_rooms()
    return jsonify(rooms), 200

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': 'Phone number is required'}), 400

    deleted_count = db.delete_user(phone)
    if deleted_count > 0:
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/delete_room', methods=['DELETE'])
def delete_room():
    data = request.get_json()
    room_name = data.get('room_name')

    if not room_name:
        return jsonify({'message': 'Room name is required'}), 400

    deleted_count = db.delete_room(room_name)
    if deleted_count > 0:
        return jsonify({'message': 'Room deleted successfully'}), 200
    else:
        return jsonify({'message': 'Room not found'}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
