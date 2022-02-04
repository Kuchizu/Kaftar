import socket
from threading import Thread
from time import ctime, sleep

LOCALHOST = socket.gethostbyname(socket.gethostname())
PORT = 9090

threads = []
chat = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((LOCALHOST, PORT))
print(f'Started server {ctime()}')

def now_time():
    return ctime().split()[-2]

def send_all():
    while True:
        try:
            s = input()
            for i in threads:
                i.send(s)
        except Exception as e:
            print(repr(e))
            break

# cd Desktop/Socket
# cls

class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)
        self.csocket = clientsocket
        print(f'New connection: {clientAddress}')
        print(threads)
        self.broadcast(f'[{clientAddress[1]} Joinded to chat]', '[Information]')

        # print(chat)
        # for time, who, message in chat:
        #     self.csocket.sendall(bytes(f'[{time}][{who}]: {message}', 'UTF-8'))
        # Fix it lmao

    def run(self):
        global chat
        while True:
            try:
                data = self.csocket.recv(4096).decode()
            except Exception as e:
                print(repr(e))
                self.broadcast(f'[{clientAddress[1]} Left from chat]', '[Information]')
                threads.remove(self)
                print(threads)
                break

            chat += [[now_time(), clientAddress[1], data]]
            self.broadcast(data, clientAddress[1])

    def broadcast(self, msg, who='Server'):
        for client in threads:
            if client != self:
                client.csocket.send(bytes(f'[{now_time()}][{who}]: {msg}', 'UTF-8'))

# Thread(target=send_all).start()
while True:
    try:
        server.listen(10)
        clientSock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientSock)
        newthread.start()
        threads.append(newthread)
    except Exception as e:
        print(repr(e))
        # server.close()
        break
