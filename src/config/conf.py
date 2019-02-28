import pickle
global config
channel_list = open("channel_list.txt", "rb")


config = {

    # details required to login to twitch IRC server
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': '<get-username-from-twitch>', # your twitch username
    'oauth_password': '<get-key-from-twitch>',  # get this from http://twitchapps.com/tmi/

    # channel to join
    'channels': pickle.load(channel_list).read().split(','),

         # if set to true will display any data received
    'debug': False,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 4096,

    # kafka config - for multiple kafka hosts use comma separated values
    'kafka_brokers': ['localhost:9092'],
    # kafka topic
    'kafka_topic': 'twitch-parsed-message'
}
