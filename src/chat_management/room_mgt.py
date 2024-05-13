import json
import asyncio

from eventlet import websocket

connected = {}
async def leave(websocket):
    if websocket in connected:
        nickname = connected[websocket]['nickname']
        room = connected[websocket]['room']
        leave_message = json.dumps({
            "type": "system",
            "message": f"{nickname} has left the room."
        })
        print(f"{nickname} has left the chat room {room}.")
        del connected[websocket]
        # Notify other clients in the same room
        tasks = [asyncio.create_task(client.send(leave_message)) for client in connected
                 if connected[client]['room'] == room]
        if tasks:
            await asyncio.wait(tasks)
        else:
            print("No other clients in the room, no broadcast needed.")
if __name__ == '__main__':
    asyncio.run(leave(websocket))