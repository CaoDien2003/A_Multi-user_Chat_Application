import asyncio
import websockets
import json
from src.UsersAuthentication.database.storage_users import MongoDB
from src.chat_management.room_mgt import ChatManager

db = MongoDB('mongodb://localhost:27017/')
chat_manager = ChatManager()

async def handle_client(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received message: {data}")  # Debugging print
            if data['action'] == 'authenticate':
                token = data['token']
                user = db.get_by_token(token)
                if user:
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication successful"}))
                    print(f"User authenticated: {user['name']}")
                else:
                    await websocket.send(json.dumps({"type": "system", "message": "Authentication failed"}))
                    await websocket.close()
                    print("Authentication failed")
            elif data['action'] == 'join':
                await chat_manager.join(websocket, data['nickname'], data['room'])
            elif data['action'] == 'leave':
                await chat_manager.leave(websocket)
                await websocket.close()
            elif data['action'] == 'create_room':
                await chat_manager.create_room(data['room'])
            elif data['action'] == 'message':
                await chat_manager.broadcast_message(websocket, data['message'])
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected abruptly")
        await chat_manager.leave(websocket)
    except Exception as e:
        print(f"Error: {e}")
        import pdb; pdb.set_trace()  # Debugging breakpoint

async def main():
    print("Starting WebSocket server on ws://localhost:6789")
    async with websockets.serve(handle_client, "localhost", 6789):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
