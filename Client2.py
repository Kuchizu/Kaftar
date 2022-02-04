import socket
import PySimpleGUI as sg
from threading import Thread

SERVER = "62.109.4.22"
PORT = 9090

layout = [
    [sg.MLine(size=(80, 20), key='textbox')],
    [sg.Text('Text: '), sg.InputText(do_not_clear=False), sg.Submit('Send')],
]

window = sg.Window('Socktogram', layout)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print(f'Successfuly connected to {SERVER}, port {PORT}.')

def listen():
    while True:
        try:
            in_data = client.recv(4096).decode()
            window['textbox'].print(f'{in_data}')
        except (KeyboardInterrupt, ConnectionResetError):
            client.close()
            break

def rec():
    while True:
        try:
            out_data = input()
            client.sendall(bytes(out_data, 'UTF-8'))
        except (KeyboardInterrupt, ConnectionResetError):
            client.close()
            break

def gui():
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            client.close()
            break
        # print(window['textbox'])
        # print(dir(window['textbox']))
        # print(window['textbox']['AutoSizeText'])
        if event in ('Send'):
            window['textbox'].print(f'Me: {values[0]}')
            client.sendall(bytes(values[0], 'UTF-8'))



lisT = Thread(target=listen).start()
recT = Thread(target=rec).start()
winT = Thread(target=gui).start()
