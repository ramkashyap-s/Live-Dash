import logging
from emoji import demojize
from kafka import KafkaProducer
import json
from time import gmtime, strftime
from src.config.conf import *

server = 'irc.chat.twitch.tv'
port = 6667
nickname = 'srk3141'
token = 'oauth:stohe9j4evimw08quy46nm5htphllu'
channels = ['#trainwreckstv', '#macaiyla', '#therealshookon3']
#channels: rockitsage, deamonmachine, phantomcode32, #moondye7
import socket
from time import gmtime, strftime

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
twitchtopic_producer = KafkaProducer(bootstrap_servers=config['kafka_config'],
                                          api_version=(0, 10, 2), key_serializer=lambda m: str.encode(m),
                                          value_serializer=lambda m: json.dumps(m).encode('utf-8'))

message_count = 0
while True:
    resp = sock.recv(2048).decode('utf-8')

    if resp.startswith('PING'):
        sock.send("PONG\n".encode('utf-8'))

    elif len(resp) > 0:
        resp_clean = resp.strip()
        message_count += 1
        # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + demojize(resp_clean) + "messages:" + str(message_count))
        twitchtopic_producer.send('twitch-message', key=channel, value=resp_clean)

