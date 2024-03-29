import socket
import PySimpleGUI as sg
from threading import Thread
from time import ctime, sleep
from pickle import dumps, loads
from random import randint

SERVER = socket.gethostbyname(socket.gethostname())  # "62.109.4.22"
PORT = 9090
justif = lambda x: ' ' * x
nowtime = lambda: ctime().split()[-2]
Me = None
sg.theme('DarkGrey10')
font = ("Arial, 14")
smaller_font = ("Arial, 11")
smaller_font2 = ("Arial, 9")
small = ("Arial, 7")
sg.set_options(font=font)


class User:
    def __init__(self, user_id, user_name):
        self.id = user_id
        self.name = user_name


# Fucking layouts
layout1 = [
    [
        sg.Text(
            text='Welcome to Kaftar!',
            relief=sg.RELIEF_RAISED
        )
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
        sg.Column(
            layout=[],
            scrollable=True,
            vertical_scroll_only=True,
            size=(270, 147 * 3),
            key='-Chatlist-'
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
            text=justif(60) + 'Input: ',
            justification='right'
            # expand_x=True
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
            visible=True,
        ),
        sg.Column(
            layout=layout2,
            key='-Win_Reg-',
            vertical_alignment='center',
            element_justification='l',
            visible=False
        ),
        sg.Column(
            layout=layout3,
            key='-Win_Main-',
            visible=True
        )
    ]
]

cur_lay = '-Win_Login-'
cur_chat = None
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

            if cmd == 'Loadchatlist':
                Me = User(*data[1])
                window.write_event_value('-LoadchatsThread-', data[2])

            if cmd == 'Loadchat':
                window.write_event_value('-LoadThread-', data[1])

            if cmd == 'Message':
                from_id, from_name = data[1]
                message = data[2]
                window.write_event_value('-PrintThread-', [from_id, from_name, data[2]])

        except Exception as e:
            print('Listen: ', repr(e))
            break


def gui(lisT):
    global window, cur_lay, cur_chat
    chatlist = {}
    window = sg.Window('Kaftar', layout, finalize=True)
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit', 'Cancel'):
            client.sendall(dumps(['Killme']))
            break

        if event in ('Send') and values['-Input-'] and cur_chat:
            message = values['-Input-']
            window['textbox'].print(f"[{nowtime()}][{Me.name}]: {message}")
            client.sendall(dumps(['Send', cur_chat, [Me.id, Me.name], message]))

            q = sg.Column(
                layout=[[sg.Text('1')]],
                scrollable=True,
                vertical_scroll_only=True,
                size=(270, 147 * 3),
                key='-Chatlist-'
            )
            # window['-Chatlist-'] = 1
            print(window['-Chatlist-'])
            # print('YEYAEIDDN')

        if event in ('-LoadchatsThread-'):
            chats = values['-LoadchatsThread-']
            print(chats)
            for chat_id, when, last_message, who in chats:
                window.extend_layout(
                    window['-Chatlist-'],
                    [
                        [
                            sg.Frame(
                                title=who,
                                layout=
                                [
                                    [
                                        sg.Text(
                                            text=when.strftime('%H:%M:%S'),
                                            font=smaller_font2
                                        ),
                                        sg.Text(
                                            text=f'{last_message[:15]}...'
                                            if len(last_message) > 15 else last_message
                                        ),
                                    ]
                                ],
                                pad=(0, 0),
                                expand_x=True,
                                # relief=sg.RELIEF_FLAT,
                                key=f'Frame:{chat_id}'
                            )
                        ]
                    ]
                )
                chatlist[chat_id] = who
                window[f'Frame:{chat_id}'].bind('<Button-1>', '')

        if event in ('-LoadThread-'):
            pm_chat = values['-LoadThread-']
            for from_id, date, message in pm_chat:
                date = date.strftime('%H:%M:%S')
                who = Me.name if from_id == Me.id else chatlist[from_id]
                window['textbox'].print(f'[{date}][{who}]: {message}')

        if event in ('-PrintThread-'):
            from_chat, from_name, message = values['-PrintThread-']
            print(from_chat, cur_chat)
            if from_chat == cur_chat:
                window['textbox'].print(f'[{nowtime()}][{from_name}]: {message}')

        if 'Frame' in event:
            print(window['-Chatlist-'].update())
            cur_chat = int(event.split(':')[-1])
            window['textbox'].update('')
            client.sendall(dumps(['Loadchat', cur_chat, Me.id]))

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
Thread(target=gui, args=(lisT,)).start()
