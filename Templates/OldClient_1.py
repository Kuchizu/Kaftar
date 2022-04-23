import socket
import PySimpleGUI as sg
from threading import Thread
from time import ctime, sleep
from pickle import dumps, loads

SERVER = socket.gethostbyname(socket.gethostname()) # "62.109.4.22"
PORT = 9090
justif = lambda x: ' ' * x
nowtime = lambda: ctime().split()[-2]
Me = None
sg.theme('DarkGrey10')
font = ("Arial, 14")
sg.set_options(font=font)

class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

# Fucking layouts
layout1 = [
    [
        sg.Text('Welcome to Kaftar!')
    ],
    [
        sg.Text('Login:' + justif(8)),
        sg.InputText(key='-Login-')
    ],
    [
        sg.Text('Password:' + justif(1)),
        sg.InputText(key='-Password-')
    ],
    [
        sg.Button('Log in'),
        sg.Button('-Register-')
    ],
]

layout2 = [
    [
        sg.Text(justif(40) + 'Welcome to Kaftar!')
    ],
    [
        sg.Text('Number:' + justif(16)),
        sg.InputText(key='-Reg_number-')
    ],
    [
        sg.Text('Login:' + justif(19)),
        sg.InputText(key='-Reg_login-')
    ],
    [
        sg.Text('Password:' + justif(13)),
        sg.InputText(key='-Reg_password-')
    ],
    [
        sg.Text('Name' + justif(2)),
        sg.InputText(key='-Reg_name-')
    ],
    [
        sg.Button('Back', key='-Login_back-'),
        sg.Button('Register', key='-Registrate-')
    ],
]

layout3 = [
    [
        sg.Listbox(
            values=[],
            key='-Chats-',
            auto_size_text=True,
            size=(10, 18),
            no_scrollbar=True,
            enable_events=True
        ),
        sg.MLine(
            size=(70, 20),
            key='textbox',
            focus=True,
            write_only=True
        )
    ],
    [
        sg.Text(
            text=justif(40) + 'Input: ',
            justification='right'
        ),
        sg.InputText(
            do_not_clear=False,
            key='-Input-'
        ),
        sg.Submit('Send')
    ],
]

layout = [
    [
        sg.Column(
            layout=layout1,
            key='-Win_Login-',
            element_justification='center',
            visible = True
        ),
        sg.Column(
            layout=layout2,
            key='-Win_Reg-',
            vertical_alignment='center',
            element_justification='l',
            visible = False
        ),
        sg.Column(
            layout=layout3,
            key='-Win_Main-',
            visible = True
        )
    ]
]


cur_lay = '-Win_Login-'
window = sg.Window('Kaftar', layout)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
print(f'Successfuly connected to {SERVER}, port {PORT}.')

def listen():
    sleep(0.5)
    global Me
    while True:
        try:
            data = loads(client.recv(4096))
            cmd = data[0]

            if cmd == 'Kill':
                break

            if cmd == 'Login':
                if not data[1]:
                    window.write_event_value('-LoginThread-', {'ok': False, 'err': data[2]})
                else:
                    window.write_event_value('-LoginThread-', {'ok': True})

            if cmd == 'Loadchats':
                Me = User(*data[1])
                window.write_event_value('-LoadchatsThread-', [*data[2], *data[3]])

            if cmd == 'Loadpm':
                window.write_event_value('-LoadThread-', data[1])

            if cmd == 'Message':
                from_id, from_name = data[1]
                message = data[2]
                window.write_event_value('-PrintThread-', [from_id, from_name, data[2]])

        except Exception as e:
            print('Listen: ', repr(e))
            break

def gui(lisT):
    user_ids, user_names, group_ids, group_names = [], [], [], []
    chats, titles = [], []
    while True:
        global cur_lay
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            client.sendall(dumps(['Killme']))
            break

        if event in ('Send') and values['-Input-'] and values['-Chats-']:
            message = values['-Input-']
            window['textbox'].print(f"[{nowtime()}][{Me.name}]: {message}")
            to_id = meta[chats.index(values['-Chats-'][0])]
            client.sendall(dumps(['Send', to_id, [Me.id, Me.name], message]))

        if event in ('-LoadchatsThread-'):
            user_ids, user_names, group_ids, group_names = values['-LoadchatsThread-']
            window['-Chats-'].update(values=user_names + group_names)

        if event in ('-LoadThread-'):
            pm_chat = values['-LoadThread-']
            for from_id, date, message in pm_chat:
                date = date.strftime('%H:%M:%S')
                who = Me.name if from_id == Me.id else values['-Chats-'][0]
                window['textbox'].print(f'[{date}][{who}]: {message}')

        if event in ('-PrintThread-') and values['-Chats-']:
            now_chat = meta[chats.index(values['-Chats-'][0])]
            from_id, from_name, message = values['-PrintThread-']
            if from_id == now_chat:
                window['textbox'].print(f'[{nowtime()}][{from_name}]: {message}')

        if event in ('-Chats-') and values['-Chats-']:
            continue
            window['textbox'].update('')
            with_id = meta[chats.index(values['-Chats-'][0])] # Придумай что-нибудь с этой хуйнёй ну нельзя же так
            client.sendall(dumps(['Loadpm', with_id, Me.id]))
            pass

        if event in ('-Login_back-'):
            window[cur_lay].update(visible=False)
            cur_lay = '-Win_Login-'
            window[cur_lay].update(visible=True)

        if event in ('Log in'):
            login = values['-Login-']
            password = values['-Password-']
            if not login:
                sg.popup_error('Login not filled.')
            elif not password:
                sg.popup_error('Password not filled.')
            else:
                print('Sent')
                client.sendall(dumps(['Login', login, password]))

        if event in ('-LoginThread-'):
            if not values['-LoginThread-']['ok']:
                sg.popup_error(values['-LoginThread-']['err'])
            else:
                window[cur_lay].update(visible=False)
                cur_lay = '-Win_Main-'
                window[cur_lay].update(visible=True)


        if event in ('-Registrate-'):
            number = values['-Number-']
            name = values['-Name-']
            password = values['-Password-']
            surname = values['-Surname-']
            username = values['-Username-']
            if not number or not number[2:].isdigit():
                sg.popup_error('Invalid phone number.')
            elif not name:
                sg.popup_error('Name not filled.')
            elif not password:
                sg.popup_error('Password not filled')
            else:
                pass

            print(number, name, password, surname, username, sep='\n')

        if event in ('-Register-'):
            window[cur_lay].update(visible=False)
            cur_lay = '-Win_Reg-'
            window[cur_lay].update(visible=True)

        # if event in '12':
        #     window[f'-COL{cur_lay}-'].update(visible=False)
        #     cur_lay = int(event[0])
        #     print(cur_lay)
        #     window[f'-COL{cur_lay}-'].update(visible=True)

lisT = Thread(target=listen)
lisT.start()
Thread(target=gui, args = (lisT, )).start()
