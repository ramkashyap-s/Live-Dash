"""
Simple IRC Bot for Twitch.tv

Developed by Aidan Thomson <aidraj0@gmail.com>

Adapted by Ram
"""

from src.twitchbot import irc as irc_
import time
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from collections import *


class ReaderBot:

    def __init__(self, config):
        self.config = config
        self.irc = irc_.irc(config)
        self.socket = self.irc.get_irc_socket_object()

    # def num_comments(self, messages):
    # def num_users(self, messages):
    def nltk_sentiment(sentence):
        nltk_sentiment = SentimentIntensityAnalyzer()
        score = nltk_sentiment.polarity_scores(sentence)
        return score

    def run(self):
        irc = self.irc
        sock = self.socket
        config = self.config
        user_counter = [Counter() for i in range(len(config['channels']))]
        user_interactions = defaultdict(None, zip(config['channels'], user_counter))
        num_comments = defaultdict(int)
        num_user_interactions = defaultdict(int)
        channel_sentiment = defaultdict()
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > 10:
                # reset start_time
                print(list(num_user_interactions.items()))
                print(list(num_comments.items()))
                print("start new window")
                user_counter = [Counter() for i in range(len(config['channels']))]
                user_interactions = defaultdict(None, zip(config['channels'], user_counter))
                num_comments = defaultdict(int)
                num_user_interactions = defaultdict(int)
                start_time = time.time()


            data = sock.recv(config['socket_buffer_size']).rstrip()
            data = data.decode('utf-8','ignore')
            if len(data) == 0:
                print('Connection was lost, reconnecting.')
                self.socket = self.irc.get_irc_socket_object()

            if config['debug']:
                print(data)

            # check for ping, reply with pong
            irc.check_for_ping(data)
            
            if irc.check_for_message(data):
                message_dict = irc.get_message(data)
                num_comments[message_dict['channel']] += 1
                user_interactions[message_dict['channel']][message_dict['username']] += 1
                num_user_interactions[message_dict['channel']] = \
                    (len(user_interactions.get(message_dict['channel'])))


                # self.nltk_sentiment(message_dict['message'])
                # channel_sentiment.get(message_dict['channel'], self.nltk_sentiment(message_dict['message']))
                # print(message_dict['channel'], user_interactions.get(message_dict['channel']))
                # print(message_dict)
                # print(len(user_interactions.get(message_dict['channel'])))
                # message = message_dict['message']
                # username = message_dict['username']
                # self.chat_topic.send('new_chatmessage', str.encode(json.dumps(message_dict)))



