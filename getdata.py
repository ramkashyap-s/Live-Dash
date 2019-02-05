import logging
from emoji import demojize

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'srk3141'
token = 'oauth:stohe9j4evimw08quy46nm5htphllu'
channels = ["#deamonmachine", "#clawontwitch"]
#channels: rockitsage, deamonmachine, phantomcode32, #moondye7
import socket

sock = socket.socket()
sock.connect((server, port))

sock.send(f"PASS {token}\n".encode('utf-8'))
sock.send(f"NICK {nickname}\n".encode('utf-8'))
for channel in channels:
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s — %(message)s',
#                     datefmt='%Y-%m-%d_%H:%M:%S',
#                     handlers=[logging.FileHandler('chat.log', encoding='utf-8')])

# if (sock.recv(2048).decode('utf-8')):
#     print('Login successful.')

while True:
    resp = sock.recv(2048).decode('utf-8')

    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))

    elif len(resp) > 0:
        resp_clean = resp.strip()
        # print(resp_clean)
        print(demojize(resp_clean))
