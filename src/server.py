import asyncio
import websockets

connected = set()

async def chat_server(websocket, path):
    # Receive the nickname as the first message from the client.
    nickname = await websocket.recv()
    print(f"{nickname} has joined the chat!")
    connected.add(websocket)
    await websocket.send("You are now connected.")
    
    try:
        # Process incoming messages
        async for message in websocket:
            formatted_message = f"{nickname}: {message}"
            print(f"Broadcasting message: {formatted_message}")
            tasks = [asyncio.create_task(client.send(formatted_message)) for client in connected]
            await asyncio.wait(tasks)
    except websockets.exceptions.ConnectionClosed:
        print(f"{nickname} has disconnected.")
    finally:
        # Unregister the client on disconnection.
        connected.remove(websocket)

# Starting the WebSocket server
async def main():
    async with websockets.serve(chat_server, "localhost", 6789, ping_interval=None):
        await asyncio.Future()  # Run forever

asyncio.run(main())
