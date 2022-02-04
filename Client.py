import socket
from threading import Thread

SERVER = '192.168.1.10' # 62.109.4.22 192.168.1.10
PORT = 9090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print(f'Successfuly connected to {SERVER}, port {PORT}.')

def listen():
    while True:
        try:
            in_data = client.recv(4096)
            print(f'{in_data.decode()}')
        except Exception as e:
            print(repr(e))
            exit()

def rec():
    while True:
        try:
            out_data = input()
            client.sendall(bytes(out_data, 'UTF-8'))
        except Exception as e:
            print(repr(e))
            exit()

lisT = Thread(target=listen).start()
recT = Thread(target=rec).start()
