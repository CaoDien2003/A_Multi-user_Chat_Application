import asyncio
import websockets
import json
from aiohttp import web
from storage_users import MongoDB
import secrets
from flask import Flask, request, jsonify, make_response
from aiohttp_wsgi import WSGIHandler
import logging
from bson import ObjectId
from flask_cors import CORS

connected = {}

async def chat_server(websocket, path):
    try:
        # Receive initial nickname and set up user details
        logging.debug("Attempting to receive a message")
        nickname = await websocket.recv()
        logging.debug(f"{nickname} has joined the chat")
        connected[websocket] = {'nickname': nickname}
        await websocket.send(json.dumps({"type": "system", "message": "You are now connected."}))

        # Message loop
        async for message in websocket:
            formatted_message = json.dumps({
                "type": "chat",
                "nickname": connected[websocket]['nickname'],  # Fetch nickname from stored details
                "message": message
            })
            print(f"Broadcasting message from {nickname}: {message}")
            # Send to all connected clients except sender
            tasks = [asyncio.create_task(client.send(formatted_message)) for client in connected if client != websocket]
            if tasks:
                await asyncio.wait(tasks)
            else:
                print("No other clients connected, no broadcast needed.")

    except websockets.exceptions.ConnectionClosed:
        print(f"{nickname} has disconnected.")
    except Exception as e:
        logging.error("Error in chat_server: %s", str(e))
    finally:
        logging.debug(f"Cleaning up connection for {nickname}")
        # Cleanup on disconnect
        if websocket in connected:
            del connected[websocket]
            print(f"{nickname} has disconnected and cleaned up.")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.json_encoder = CustomJSONEncoder

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
            return jsonify({'token': token, 'user_info': user_info})
        else:
            return jsonify({'message': 'wrong password'}), 401
    else:
        return jsonify({'message': 'Account has not been created'}), 404

@app.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == 'POST':
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
            new_user['_id'] = str(new_user['_id'])  # Convert ObjectId to string
            return jsonify(new_user), 201
        pass

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@app.before_request
def log_request_info():
    logging.debug('Full Path: %s', request.full_path)
    logging.debug('Headers: %s', request.headers)
    logging.debug('Body: %s', request.get_data())
    logging.debug('Request path: %s', request.path)
    logging.debug('Method: %s', request.method)

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

# Run WebSocket server
async def websocket_app():
    async with websockets.serve(chat_server, "localhost", 6789, ping_interval=None):
        await asyncio.Future()  # Run forever

async def start_web_app(app, loop):
    try:
        wsgi_handler = WSGIHandler(app)
        web_app = web.Application()
        web_app.router.add_route('*', '/{path_info:.*}', wsgi_handler)
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 5000)
        await site.start()
        logging.info("Flask app running on http://localhost:5000")
    except Exception as e:
        logging.error("Failed to start Flask app: %s", str(e))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    loop = asyncio.get_event_loop()
    try:
        await asyncio.gather(
            start_web_app(app, loop),
            websockets.serve(chat_server, "localhost", 6789, ping_interval=None)
        )
        await asyncio.Future()  # This line will keep your application running
    except Exception as e:
        logging.error("An error occurred: %s", str(e))
    except ConnectionResetError:
        print("Connection was reset by the peer.")
    except asyncio.CancelledError:
        print("Connection cancelled.")

if __name__ == '__main__':
    asyncio.run(main())
