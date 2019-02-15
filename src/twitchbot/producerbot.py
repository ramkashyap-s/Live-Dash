"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>

Adapted by Ram
"""

from src.twitchbot import irc as irc_
from kafka import KafkaProducer
import json

class ProducerBot:

    def __init__(self, config):
        self.config = config
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object()
        self.twitchtopic_producer = KafkaProducer(bootstrap_servers=config['kafka_config'],
                                                api_version=(0, 8, 2), key_serializer=lambda m: str.encode(m),
                                                value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    # def on_send_success(record_metadata):
    #     print(record_metadata.topic)
    #     print(record_metadata.partition)
    #     print(record_metadata.offset)

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config

        while True:

            data = sock.recv(config['socket_buffer_size']).rstrip()
            data = data.decode('utf-8','ignore')
            if len(data) == 0:
                print('Connection was lost, reconnecting.')
                self.socket = self.irc.get_irc_socket_object()

            if config['debug']:
                print(data)

            # check for ping, reply with pong
            # irc.check_for_ping(data)


            if irc.check_for_message(data):
                message_dict = irc.get_message(data)
                channel = message_dict['channel']
                # message = message_dict['message']
                # username = message_dict['username']
                # self.chat_topic.send('new_chatmessage', str.encode(json.dumps(message_dict)))
                self.twitchtopic_producer.send('twitch-message', key=channel, value=message_dict)
                    #\ .add_callback(self.on_send_success)

    #
    # def on_send_error(excp):
    #     log.error('I am an errback', exc_info=excp)
    #     # handle exception
