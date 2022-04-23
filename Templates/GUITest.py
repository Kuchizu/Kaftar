import PySimpleGUI as sg

def Text(size):
    return sg.Text('', size=size, relief=sg.RELIEF_RAISED)

def frame():
    return [
        [sg.Text('OK:'),         sg.Push(), Text(10)],
        [sg.Text('NG:'),         sg.Push(), Text(10)],
        [sg.Text('Yield Rate:'), sg.Push(), Text(15)],
        [sg.Text('Total:'),      sg.Push(), Text(15)],
    ]

font = ('Courier New', 11)
sg.theme('DarkBlue3')
sg.set_options(font=font)

column = [
    [sg.Frame(f'AI-{i}', frame(), pad=(0, 0), key=f'FRAME {i}')]
        for i in range(1, 11)
]

layout = [
    [sg.Text('RESULT', justification='center', background_color='#424f5e', expand_x=True)],
    [sg.Column(column, scrollable=True, vertical_scroll_only=True,
        size=(270+16, 129*3), key='COLUMN')],     # width of scrollbar is 16 pixels
]

window = sg.Window('Matplotlib', layout, finalize=True)
print(window['FRAME 1'].get_size())              # get frame size in pixels (270, 129)
window.read(close=True)
