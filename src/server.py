import asyncio
import json
import websockets
from src.UsersAuthentication.database.storage import MongoDB
from src.chat_management.room_mgt import ChatManager

db = MongoDB('mongodb://localhost:27017/')
chat_manager = ChatManager()

connected_clients = set()

def generate_room_name(*users):
    return '_'.join(sorted(users))

async def handle_client(websocket, path):
    print("New client connected")
    connected_clients.add((websocket, None))
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received message: {data}")  # Debugging print
            if data['action'] == 'authenticate':
                token = data['token']
                user = db.get_by_token(token)
                print(f"User object: {user}")  # Debugging print
                if user and 'name' in user:
                    if (websocket, None) in connected_clients:
                        connected_clients.remove((websocket, None))
                    connected_clients.add((websocket, user['name']))
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication successful", "username": user['name']}))
                    print(f"User authenticated: {user['name']}")
                else:
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication failed"}))
                    await websocket.close()
                    print("Authentication failed")
            elif data['action'] == 'join':
                print(f"Joining room: {data['room']} with username: {data['username']}")
                await chat_manager.join(websocket, data['username'], data['room'])
            elif data['action'] == 'leave':
                await chat_manager.leave(websocket)
                await websocket.close()
            elif data['action'] == 'create_room':
                print(f"Creating room: {data['room']}")
                await chat_manager.create_room(data['room'])
            elif data['action'] == 'message':
                await chat_manager.broadcast_message(websocket, data['message'])
            elif data['action'] == 'private_message':
                if 'sender' in data and 'receiver' in data:
                    room = generate_room_name(data['sender'], data['receiver'])
                    print(f"Generated room: {room} for sender: {data['sender']} and receiver: {data['receiver']} with message: {data['message']}")  # Debugging print
                    await chat_manager.send_private_message(room, data['message'], websocket)
                else:
                    print("Error: Missing 'sender' or 'receiver' in private message")
            elif data['action'] == 'create_group_chat':
                group_name = data['groupName']
                users = data['users']
                room = generate_room_name(group_name, *users)
                print(f"Creating group chat room: {room} with users: {users}")
                await chat_manager.create_group_room(room, users)
                for user in users:
                    user_websocket = next((client[0] for client in connected_clients if client[1] == user), None)
                    if user_websocket:
                        await chat_manager.join(user_websocket, user, room)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected abruptly")
    finally:
        connected_clients.discard((websocket, None))
        await chat_manager.leave(websocket)
        print("Client connection closed")

async def main():
    print("Starting WebSocket server on ws://localhost:6789")
    async with websockets.serve(handle_client, "localhost", 6789):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())