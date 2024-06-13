import asyncio
import json
import websockets
from src.UsersAuthentication.database.storage import MongoDB
from src.chat_management.room_mgt import ChatManager

db = MongoDB('mongodb://localhost:27017/')
chat_manager = ChatManager()

connected_clients = set()

def generate_room_name(*users):
    # Filter out None values and sort the list of users
    return '_'.join(sorted(user for user in users if user is not None))

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
                if user and 'phone' in user:
                    if (websocket, None) in connected_clients:
                        connected_clients.remove((websocket, None))
                    connected_clients.add((websocket, user['phone']))
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication successful", "userPhone": user['phone'], "userName": user['name']}))
                    print(f"User authenticated: {user['phone']}")
                else:
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication failed"}))
                    await websocket.close()
                    print("Authentication failed")
            elif data['action'] == 'private_message':
                sender_phone = data.get('sender_phone')
                receiver_phone = data.get('receiver_phone')
                if sender_phone is None or receiver_phone is None:
                    print("Error: 'sender_phone' or 'receiver_phone' is None")
                else:
                    room = generate_room_name(sender_phone, receiver_phone)
                    receiver = db.get_by_phone(receiver_phone)
                    if receiver:
                        sender = db.get_by_phone(sender_phone)
                        if sender:
                            print(f"Handling private message in room {room}")
                            await chat_manager.send_private_message(room, data['message'], websocket, sender['name'])
                        else:
                            print("Error: Sender not found")
                    else:
                        print("Error: Receiver not found")
            elif data['action'] == 'join_room':
                username = data.get('username')
                room = data.get('room')
                if username and room:
                    print(f"Joining room: {room} with username: {username}")
                    await chat_manager.join(websocket, username, room)
                else:
                    print("Error: Missing 'username' or 'room' in join_room request")
            elif data['action'] == 'leave':
                await chat_manager.leave(websocket)
                await websocket.close()
            elif data['action'] == 'create_room':
                room = data.get('room')
                if room:
                    print(f"Creating room: {room}")
                    await chat_manager.create_room(room)
                else:
                    print("Error: Missing 'room' in create_room request")
            elif data['action'] == 'message':
                message = data.get('message')
                room = data.get('room')
                sender_name = data.get('sender_name')
                if message and room and sender_name:
                    await chat_manager.broadcast_message(websocket, message, room, sender_name)
                else:
                    print("Error: Missing 'message', 'room', or 'sender_name' in broadcast request")
            elif data['action'] == 'create_group_chat':
                group_name = data.get('groupName')
                users = data.get('users')
                if group_name and users and all(user is not None for user in users):
                    room = group_name  # Use the group name as the room name directly
                    print(f"Creating group chat room: {room} with users: {users}")
                    await chat_manager.create_group_room(room, users)
                    for user in users:
                        user_websocket = next((client[0] for client in connected_clients if client[1] == user), None)
                        if user_websocket:
                            await chat_manager.join(user_websocket, user, room)
                else:
                    print("Error: Missing 'groupName' or 'users' or one or more users are None in create_group_chat request")

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

