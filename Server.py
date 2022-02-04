import socket
from threading import Thread
from time import ctime

LOCALHOST = socket.gethostbyname(socket.gethostname())
PORT = 8080

threads = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((LOCALHOST, PORT))
print(f'Started server {ctime()}')

def send_all():
    while True:
        try:
            s = input()
            for i in threads:
                i.send(s)
        except (KeyboardInterrupt, EOFError):
            server.close()
            break

class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)
        self.csocket = clientsocket
        print(f'New connection: {clientAddress}')

    def run(self):
        msg = ''
        while True:
            try:
                data = self.csocket.recv(4096)
            except (KeyboardInterrupt, ConnectionResetError):
                server.close()
                break
            msg = data.decode()
            for i in threads:
                if i != self:
                    i.send(msg)
            if not msg:
                print('Disconnected.')
                break

            if msg == 'kal':
                self.csocket.send(bytes('Hudat kal', 'UTF-8'))

    def send(self, msg, who='Server'):
        self.csocket.send(bytes(f'{who}: {msg}', 'UTF-8'))

# Thread(target=send_all).start()
while True:
    try:
        server.listen(1)
        clientSock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientSock)
        newthread.start()
        threads.append(newthread)
    except KeyboardInterrupt:
        server.close()
        break
