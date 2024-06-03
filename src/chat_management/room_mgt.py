import asyncio
import json

class ChatManager:
    def __init__(self):
        self.rooms = {}

    async def join(self, websocket, nickname, room):
        print(f"Joining room: {room}, Nickname: {nickname}")
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append((websocket, nickname))
        join_message = json.dumps({
            "type": "system",
            "message": f"{nickname} has joined the room {room}."
        })
        tasks = [client[0].send(join_message) for client in self.rooms[room] if client[0] != websocket]
        await asyncio.gather(*tasks)
        print(f"Current clients in {room}: {[(client[1], id(client[0])) for client in self.rooms[room]]}")

    async def leave(self, websocket):
        for room, clients in self.rooms.items():
            for client in clients:
                if client[0] == websocket:
                    self.rooms[room].remove(client)
                    leave_message = json.dumps({
                        "type": "system",
                        "message": f"{client[1]} has left the room {room}."
                    })
                    tasks = [c[0].send(leave_message) for c in self.rooms[room]]
                    await asyncio.gather(*tasks)
                    print(f"{client[1]} has left room {room}")
                    break

    async def create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        print(f"Room {room_name} created")

    async def broadcast_message(self, websocket, message):
        sender = None
        room = None
        for r, clients in self.rooms.items():
            for client in clients:
                if client[0] == websocket:
                    sender = client[1]
                    room = r
                    break
            if sender:
                break

        if sender and room:
            broadcast_message = json.dumps({
                "type": "chat",
                "sender": sender,
                "message": message
            })
            tasks = [client[0].send(broadcast_message) for client in self.rooms[room] if client[0] != websocket]
            await asyncio.gather(*tasks)
            print(f"Broadcasted message from {sender} in room {room}: {message}")
        else:
            print("Error: Sender or room not found")
