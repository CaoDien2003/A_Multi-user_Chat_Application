import asyncio
import websockets
import json

async def receive_messages(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'chat':
                print(f"{data['sender']}: {data['message']}")
            elif data['type'] == 'system':
                print(f"System: {data['message']}")
    except websockets.ConnectionClosed:
        print("Connection closed while receiving messages.")
    except Exception as e:
        print(f"Error while receiving messages: {e}")

async def send_messages(websocket):
    while True:
        try:
            message = input("Enter your message (or type '/leave' to disconnect): ")
            if message == "/leave":
                await websocket.send(json.dumps({"action": "leave"}))
                await websocket.close()
                break
            await websocket.send(json.dumps({"action": "message", "message": message}))
        except websockets.ConnectionClosed:
            print("Connection closed while sending messages.")
            break
        except Exception as e:
            print(f"Error while sending messages: {e}")
            break

async def websocket_client():
    uri = "ws://localhost:6789"
    try:
        async with websockets.connect(uri) as websocket:
            token = input("Enter your authentication token: ")
            await websocket.send(json.dumps({"action": "authenticate", "token": token}))
            response = await websocket.recv()
            print(response)
            
            if json.loads(response).get("message") == "Authentication successful":
                nickname = input("Enter your nickname: ")
                room = input("Enter the room name to join: ")
                await websocket.send(json.dumps({"action": "join", "nickname": nickname, "room": room}))

                # Start receiving messages in a separate task
                receive_task = asyncio.create_task(receive_messages(websocket))
                
                await send_messages(websocket)
                
                # Cancel the receive task when done sending messages
                receive_task.cancel()
            else:
                print("Authentication failed. Closing connection.")
                await websocket.close()
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(websocket_client())
