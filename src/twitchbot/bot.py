"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>

Adapted by Ram
"""

from src.twitchbot import irc as irc_
from kafka import KafkaProducer
import json
from time import gmtime, strftime

class TwitchBot:

    def __init__(self, config):
        self.config = config
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object()
        self.twitchtopic_producer = KafkaProducer(bootstrap_servers=config['kafka_brokers'],
                                                api_version=(0, 10, 2), key_serializer=lambda m:str.encode(m),
                                                value_serializer=lambda m: str.encode(json.dumps(m)))

    # def on_send_success(record_metadata):
    #     print(record_metadata.topic)
    #     print(record_metadata.partition)
    #     print(record_metadata.offset)

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config

        # try:
        while True:

            data = sock.recv(config['socket_buffer_size']).decode('utf-8', errors='ignore')

            if len(data) == 0:
                print('Connection was lost, reconnecting.')
                # sock.close()
                self.socket = self.irc.get_irc_socket_object()

            if config['debug']:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + data)

            # check for ping, reply with pong
            if data.startswith('PING'):
                print(data)
                sock.send("PONG\n".encode('utf-8'))
            # irc.check_for_ping(data)

            if irc.check_for_message(data):
                message_dict = irc.get_message(data)
                channel = message_dict['channel']
                # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + data)
                # message = message_dict['message']
                # username = message_dict['username']
                # self.chat_topic.send('new_chatmessage', str.encode(json.dumps(message_dict)))
                self.twitchtopic_producer.send('twitch-message', key=channel, value=message_dict)
                # .add_callback(self.on_send_success)
        # except KeyboardInterrupt:
        #     pass



    #
    # def on_send_error(excp):
    #     log.error('I am an errback', exc_info=excp)
    #     # handle exception
