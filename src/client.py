import socket
import threading

def receive_message():
    while True:
        try:
            message = client_socket.recv(1024).decode('ascii')
            if message == 'NICK':
                client_socket.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("You have been disconnected from the server.")
            client_socket.close()
            break

def write_message():
    while True:
        message = f"{nickname}: {input('')}"
        client_socket.send(message.encode('ascii'))

nickname = input("Choose your nickname: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
client_socket.connect((host, port))

threading.Thread(target=receive_message).start()
threading.Thread(target=write_message).start()
