import socket
import PySimpleGUI as sg
from threading import Thread
from time import ctime, sleep

SERVER = "192.168.1.10"
PORT = 9090
ME = "Me"

layout = [
    [sg.MLine(size=(80, 20), key='textbox')],
    [sg.Text('Text: '), sg.InputText(do_not_clear=False), sg.Submit('Send')],
]

window = sg.Window('Socktogram', layout)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print(f'Successfuly connected to {SERVER}, port {PORT}.')

def listen():
    sleep(1)
    while True:
        try:
            in_data = client.recv(4096).decode()
            window['textbox'].print(f'{in_data}')
        except Exception as e:
            print(repr(e))
            break

def rec():
    while True:
        try:
            out_data = input()
            client.sendall(bytes(out_data, 'UTF-8'))
        except Exception as e:
            print(repr(e))
            break

def gui():
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            break
        if event in ('Send') and values[0]:
            window['textbox'].print(f'[{ctime().split()[-2]}][{ME}]: {values[0]}')
            client.sendall(bytes(values[0], 'UTF-8'))

lisT = Thread(target=listen).start()
recT = Thread(target=rec).start()
winT = Thread(target=gui).start()
