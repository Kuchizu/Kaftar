import socket
import psycopg2
from threading import Thread
from time import ctime, sleep
from pickle import dumps, loads
from datetime import datetime

print(f'Starting...  {ctime()}')
LOCALHOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
nowtime = lambda: ctime().split()[-2]

threads = {}
chat = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print(f'Connecting to PostgreSQL...  {ctime()}')

db = psycopg2.connect(
    host="62.109.4.22",
    database="kuchizuchat",
    user="kuchizu",
    port="5432",
    password="Rp858cdf8wZB"
)
cursor = db.cursor()

print(f'Connected to PostgreSQL...  {ctime()}')

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id int,
    reg_date date,
    number text,
    login text,
    password text,
    name text
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS private_chats(
    id int,
    creator_id int,
    with_id int,
    created_date date,
    visib bool not null default True
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS group_chats(
    id int,
    creator_id int,
    created_date date,
    title text,
    visib bool not null default True
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS group_conn(
    group_id int,
    user_id int,
    join_date date,
    exist bool not null default True
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS private_messages(
    message_id serial,
    from_user_id int,
    to_user_id int,
    send_date timestamp,
    message text,
    type text default 'text',
    exist bool not null default True
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS group_messages(
    message_id serial,
    group_id int,
    from_user_id int,
    send_date timestamp,
    message text,
    type text default 'text',
    exist bool not null default True
)""")

# cursor.execute('drop table group_messages')
# db.commit()
# cursor.execute('drop table groups_db')
# db.commit()
# cursor.execute('UPDATE groups_db SET id = DEFAULT;')
# cursor.execute("Select (groups_db.id.seq, 2)")
# sql_string = "Insert into groups_db (created_date, users, messages) values (%s, %s, %s)"
# cursor.execute(sql_string, (datetime.now(), [], []))
# sql_string = "Insert into users (user_id, reg_date, number, login, password, name) values (%s, %s, %s, %s, %s, %s)"
# cursor.execute(sql_string, (3, datetime.now(), '+1', 'Kaftar', 'kometa', 'Kaftar'))
# sql_string = "Insert into private_chats (id, creator_id, with_id, created_date) values (%s, %s, %s, %s)"
# cursor.execute(sql_string, (2, 1, 3, datetime.now()))
# sql_string = "Insert into group_chats (id, creator_id, created_date, title) values (%s, %s, %s, %s)"
# cursor.execute(sql_string, (-1, 1, datetime.now(), 'Global Chat'))
# sql_string = "Insert into group_conn (group_id, user_id, join_date) values (%s, %s, %s)"
# cursor.execute(sql_string, (-1, 2, datetime.now()))
# cursor.execute(sql_string, (datetime.now(), [], []))
# sql_string = "Update groups_db set messages = array_append(messages, 'Bruh') where group_id = 1"
# cursor.execute(sql_string)
# sql_string = "Update groups_db set messages = array_append(messages, 'rr') where group_id = 1"
# cursor.execute(sql_string)
# cursor.execute(sql_string)
# cursor.execute(sql_string)
# sql_string = 'Insert into group_messages (group_id, from_user_id, send_date, message) values (%s, %s, %s, %s)'
# cursor.execute(sql_string, (-1, 1, datetime.now(), 'Konpeko!'))

db.commit()

server.bind((LOCALHOST, PORT))
print(f'Server started.  {ctime()}')


def print_bd():
    cursor.execute("select * from users")
    print('Users:')
    print(cursor.fetchall())
    print()
    cursor.execute("select * from private_chats")
    print('private_chats:')
    print(cursor.fetchall())
    print()
    cursor.execute("select * from group_chats")
    print('group_chats:')
    print(cursor.fetchall())
    print()
    cursor.execute("select * from group_conn")
    print('group_conn:')
    print(cursor.fetchall())
    print()
    cursor.execute("select * from private_messages")
    print('private_messages:')
    print(cursor.fetchall())
    print()
    cursor.execute("select * from group_messages")
    print('group_messages:')
    print(cursor.fetchall())
    print()


print_bd()


class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)
        self.csocket = clientsocket
        self.id = None
        self.name = None

        print(f'New connection from: {clientAddress}  {ctime()}')

    def run(self):
        while True:
            try:
                data = loads(self.csocket.recv(4096))
                print(data)
                print(threads)
            except Exception as e:
                print(repr(e))
                if threads.get(self.id):
                    del threads[self.id]
                print(threads)
                break

            if data[0] == 'Killme':
                self.csocket.sendall(dumps(['Kill']))

            if data[0] == 'Login':
                login, password = data[1:]
                cursor.execute('Select password, user_id, name from users where login = %s', (login,))
                if not (fetch := cursor.fetchone()):
                    self.csocket.sendall(dumps(['Login', False, 'User not found.']))
                elif fetch[0] != password:
                    self.csocket.sendall(dumps(['Login', False, 'Password incorrect.']))
                else:
                    self.id, self.name = fetch[1:]
                    threads[self.id] = self
                    self.csocket.sendall(dumps(['Login', True]))
                    user_pms = []
                    cursor.execute(
                        'Select creator_id, with_id from private_chats where creator_id = %s or with_id = %s',
                        (self.id, self.id)
                    )
                    for creator_id, with_id in cursor.fetchall():
                        cursor.execute(
                            'Select send_date, message from private_messages where (from_user_id = %s and to_user_id = %s) or '
                            '(from_user_id = %s and to_user_id = %s) order by message_id DESC limit 1',
                            (creator_id, with_id, with_id, creator_id)
                        )
                        user_pms.append(
                            [
                                creator_id if creator_id != self.id else with_id, *cursor.fetchone()
                            ]
                        )
                    for ind, user_id in enumerate(user_pms):
                        cursor.execute(
                            'Select name from users where user_id = %s',
                            (user_id[0], )
                        )
                        user_pms[ind].append(cursor.fetchone()[0])
                    cursor.execute(
                        'Select group_id from group_conn where user_id = %s and exist = True',
                        (self.id, )
                    )
                    user_groups = [[i[0]] for i in cursor.fetchall()]
                    for ind, group_id in enumerate(user_groups):
                        cursor.execute(
                            'Select send_date, message from group_messages where group_id = %s order by message_id DESC limit 1',
                            (group_id[0], )
                        )
                        user_groups[ind].extend(
                            [
                                *cursor.fetchone()
                            ]
                        )
                    for ind, group_id in enumerate(user_groups):
                        cursor.execute(
                            'Select title from group_chats where id = %s',
                            (group_id[0], )
                        )
                        user_groups[ind].append(cursor.fetchone()[0])
                    user_chats = sorted(user_pms + user_groups, key = lambda x: x[1], reverse=True)
                    print(user_chats, sep='\n')
                    self.csocket.sendall(
                        dumps(['Loadchatlist', [self.id, self.name], user_chats])
                    )

            if data[0] == 'Loadchat':
                with_id, from_id = data[1:]
                if with_id > 0:
                    cursor.execute(
                        'Select from_user_id, send_date, message from private_messages where (from_user_id = %s and '
                        'to_user_id = %s) or (from_user_id = %s and to_user_id = %s)',
                        (with_id, from_id, from_id, with_id)
                    )
                    pm_chat = cursor.fetchall()  # TODO: Add Limit
                    self.csocket.sendall(dumps(['Loadchat', pm_chat]))
                else:
                    cursor.execute(
                        'Select from_user_id, send_date, message from group_messages where group_id = %s',
                        (with_id, )
                    )
                    group_chat = cursor.fetchall()
                    self.csocket.sendall(dumps(['Loadchat', group_chat]))

            if data[0] == 'Send':
                print('Sending')
                print(threads)
                to_id, from_chat, message = data[1:]
                print(to_id)
                print(threads.get(to_id))

                if to_id > 0:
                    if threads.get(to_id):
                        print('Message', threads[to_id])
                        threads[to_id].csocket.sendall(dumps(['Message', from_chat, message]))

                    cursor.execute(
                        'Insert into private_messages (from_user_id, to_user_id, send_date, message) values (%s, %s, %s, %s)',
                        (from_chat[0], to_id, datetime.now(), message)
                    )
                    db.commit()

                else:
                    cursor.execute(
                        'Select user_id from group_conn where group_id = %s and exist = True',
                        (to_id, )
                    )
                    group_users = [i[0] for i in cursor.fetchall()]
                    print(group_users)
                    for user in group_users:
                        if threads.get(user) and user != self.id:
                            print('Message', threads[user])
                            threads[user].csocket.sendall(dumps(['Message', [to_id, from_chat[1]], message]))
                    cursor.execute(
                        'Insert into group_messages (group_id, from_user_id, send_date, message) values (%s, %s, %s, %s)',
                        (to_id, from_chat[0], datetime.now(), message)
                    )
                    # TODO: # OPTIMIZE: Don't make sql request, use arrays instead.
                    db.commit()

while True:
    try:
        server.listen(10)
        clientSock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientSock)
        newthread.start()
    except Exception as e:
        print(repr(e))
        # server.close()
        break
