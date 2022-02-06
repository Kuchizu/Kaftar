import socket
import PySimpleGUI as sg
from threading import Thread
from time import ctime, sleep

SERVER = "62.109.4.22"
PORT = 9090
ME = "Me"
sg.theme('DarkGrey10')
font = ("Arial, 14")
sg.set_options(font=font)

# Fucking layouts
layout1 = [
    [sg.Text('Welcome to Socktogram!', justification='center')],
    [sg.Text('Login:' + ' ' * 8, justification='left'), sg.InputText(justification='center', key='-Login-')],
    [sg.Text('Password: ', justification='left'), sg.InputText(justification='center', key='-Register-')],
    [sg.Button('Log in'), sg.Button('Register')],
]
layout2 = [
    [sg.Listbox(['Global Chat']+[f'Одам {_}' for _ in range(10)], auto_size_text=True, size=(10, 19), no_scrollbar=True, key='-Chats-', enable_events=True), sg.MLine(size=(70, 20), key='textbox', focus=True, write_only=True)],
    [sg.Text(' ' * 40 + 'Input: ', justification='right'), sg.InputText(do_not_clear=False, key='-Input-'), sg.Submit('Send')],
]
layout = [
    [sg.Column(layout1, key='-COL1-', element_justification='center', visible = False), sg.Column(layout2, key='-COL2-', visible = True)],
]

cur_lay = 1
window = sg.Window('Socktogram', layout)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print(f'Successfuly connected to {SERVER}, port {PORT}.')

def listen():
    sleep(1)
    global cur_lay
    while True:
        try:
            in_data = client.recv(4096).decode()
            window['textbox'].print(f'{in_data}')
        except Exception as e:
            print('Listen: ', repr(e))
            break

def gui():
    while True:
        global cur_lay
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            break
        if event in ('Send') and values['-Input-']:
            print(event)
            window['textbox'].print(f"[{ctime().split()[-2]}][{ME}]: {values['-Input-']}")
            client.sendall(bytes(values['-Input-'], 'UTF-8'))

        if event in ('Log in'):
            window[f'-COL1-'].update(visible=False)
            window[f'-COL2-'].update(visible=True)

        if event in ('Register'):
            pass

        if event in '12':
            window[f'-COL{cur_lay}-'].update(visible=False)
            cur_lay = int(event[0])
            print(cur_lay)
            window[f'-COL{cur_lay}-'].update(visible=True)

    window.close()

lisT = Thread(target=listen).start()
winT = Thread(target=gui).start()
