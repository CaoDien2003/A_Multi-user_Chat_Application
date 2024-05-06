import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

response = client_socket.recv(1024)
print(response.decode())

message = input('Enter your message: ')
name = input('enter your name')

combined_message = f"{name}: {message}"
client_socket.send(combined_message.encode())

client_socket.close()
