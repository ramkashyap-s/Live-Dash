from src.twitchbot import irc as irc_
from kafka import KafkaProducer
import json
from time import gmtime, strftime


class RawBot:

    def __init__(self, config, topic):
        self.config = config
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object()
        self.twitchtopic_producer = KafkaProducer(bootstrap_servers=config['kafka_brokers'],
                                                  api_version=(0, 10, 1), key_serializer=lambda m:str.encode(m),
                                                  value_serializer=lambda m: str.encode(json.dumps(m)))
        self.topic = topic

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config

        while True:

            data = sock.recv(config['socket_buffer_size']).decode('utf-8', errors='ignore').rstrip()
            if len(data) == 0:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+'Connection was lost, reconnecting.')
                self.socket = self.irc.get_irc_socket_object()

            if config['debug']:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + data)

            # check for ping, reply with pong
            if data.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))

            # extract data and send it to kafka broker
            try:
                #message_dict = irc.get_message(data)
                #channel = message_dict['channel_name']
                channel = re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0]
                self.twitchtopic_producer.send(self.topic, key = channel, value=message_dict)
            except:
                pass
