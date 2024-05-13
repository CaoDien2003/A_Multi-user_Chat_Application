import asyncio
import json
import websockets

connected = {}
class ChatManager:
    def __init__(self):
        self.connected = {}
    async def join(self, websocket, nickname, room):
        self.connected[websocket] = {'nickname': nickname, 'room': room}
        join_message = json.dumps({
            "type": "system",
            "message": f"{nickname} has joined the room {room}."
        })
        print(f"{nickname} has joined the chat room {room}.")
        tasks = [client.send(join_message) for client in self.connected
                 if self.connected[client]['room'] == room and client != websocket]
        if tasks:
            await asyncio.gather(*tasks)
    async def leave(self, websocket):
        if websocket in self.connected:
            nickname = self.connected[websocket]['nickname']
            room = self.connected[websocket]['room']
            leave_message = json.dumps({
                "type": "system",
                "message": f"{nickname} has left the room {room}."
            })
            print(f"{nickname} has left the chat room {room}.")

            # Notify other clients in the same room
            tasks = [client.send(leave_message) for client in self.connected
                     if self.connected[client]['room'] == room and client != websocket]
            if tasks:
                await asyncio.gather(*tasks)

            del self.connected[websocket]
            await websocket.close()

