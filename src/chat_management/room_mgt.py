import asyncio
import json
import websockets

class ChatManager:
    def __init__(self):
        self.rooms = {}

    async def join(self, websocket, username, room):
        print(f"Joining room: {room}, Username: {username}")
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append((websocket, username))
        join_message = json.dumps({
            "type": "system",
            "message": f"{username} has joined the room {room}."
        })
        tasks = [self.safe_send(client[0], join_message) for client in self.rooms[room] if client[0] != websocket]
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
                    tasks = [self.safe_send(c[0], leave_message) for c in self.rooms[room]]
                    await asyncio.gather(*tasks)
                    print(f"{client[1]} has left room {room}")
                    break

    async def create_room(self, room_name):
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        print(f"Room {room_name} created")

    async def create_group_room(self, room_name, users):
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        print(f"Group room {room_name} created with users {users}")

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
            tasks = [self.safe_send(client[0], broadcast_message) for client in self.rooms[room] if client[0] != websocket]
            await asyncio.gather(*tasks)
            print(f"Broadcasted message from {sender} in room {room}: {message}")
        else:
            print("Error: Sender or room not found")

    async def send_private_message(self, room, message, websocket):
        sender = None
        if room in self.rooms:
            for client in self.rooms[room]:
                if client[0] == websocket:
                    sender = client[1]
                    break

            if sender:
                private_message = json.dumps({
                    "type": "private_chat",
                    "sender": sender,
                    "message": message
                })
                tasks = [self.safe_send(client[0], private_message) for client in self.rooms[room] if client[0] != websocket]
                await asyncio.gather(*tasks)
                print(f"Private message from {sender} in room {room}: {message}")
            else:
                print("Error: Sender not found in room")
        else:
            print(f"Error: Room {room} does not exist")

    async def safe_send(self, websocket, message):
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            print("Attempted to send a message to a closed connection")
