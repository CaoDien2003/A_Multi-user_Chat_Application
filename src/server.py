import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)

print("Server is listening...")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established!")
    client_socket.send("Welcome to the chat room!".encode())

    print(addr)
    data = client_socket.recv(1024).decode()

    name, message = data.split(':')
    print(f"{name} says: {message}")

    client_socket.close()
