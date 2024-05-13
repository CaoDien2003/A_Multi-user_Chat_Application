import asyncio
import websockets
import json
async def listen_for_messages(websocket):
    # Listen for incoming messages and print them.
    try:
        async for message in websocket:
            print(f"\n{message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server was closed.")

async def send_messages(websocket):
    # Send messages entered by the user.
    while True:
        message = input("Enter your message: ")
        if message:
            await websocket.send(message)
        if message.startswith('/create '):
            room_name = message.split(' ')[1]
            await websocket.send(json.dumps({"action": "create_room", "room": room_name}))
        elif message.startswith('/join '):
            room_name = message.split(' ')[1]
            nickname = input("Enter your nickname: ")
            await websocket.send(json.dumps({"action": "join", "nickname": nickname, "room": room_name}))
        elif message == '/leave':
            await websocket.send(json.dumps({"action": "leave"}))
        # else:
        #     print("Closing connection")
        #     break

async def websocket_client():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        nickname = input("Choose your nickname: ")
        await websocket.send(nickname)  # Send nickname as the first message after connecting.
        print(await websocket.recv())  # Receive and print the connection confirmation
        
        # Task for receiving messages
        receiver_task = asyncio.create_task(listen_for_messages(websocket))
        
        # Task for sending messages
        await send_messages(websocket)
        
        # Cleanup
        receiver_task.cancel()

if __name__ == "__main__":
    asyncio.run(websocket_client())
