import socket
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
server_socket.bind((host, port))
server_socket.listen(5)
clients = []
print("Server is listening on port:", port)

def broadcast(message, connection):
    for client in clients:
        if client != connection:
            try:
                client.send(message.encode('ascii'))
            except:
                client.close()
                remove(client)

def remove(connection):
    if connection in clients:
        clients.remove(connection)

def client_thread(conn, addr):
    conn.send('NICK'.encode('ascii'))
    nickname = conn.recv(1024).decode('ascii')
    clients.append(conn)
    print(f"Nickname of the new connection: {nickname}")
    conn.send("Welcome to the chat room!".encode('ascii'))
    while True:
        try:
            message = conn.recv(1024).decode('ascii')
            if message:
                broadcast(message, conn)
            else:
                remove(conn)
        except:
            continue

while True:
    conn, addr = server_socket.accept()
    print(f"Connection from {addr} has been established!")
    threading.Thread(target=client_thread, args=(conn, addr)).start()
