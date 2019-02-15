global config

config = {

    # details required to login to twitch IRC server
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'srk3141', # your twitch username
    'oauth_password': 'oauth:stohe9j4evimw08quy46nm5htphllu',  # get this from http://twitchapps.com/tmi/

    # channel to join '#clawontwitch', #moonmoon_ow, #neuro, #rajjpatel, #disguisedtoast,
    # #somagreen, #eevisu , #quarterjade
    'channels': ['#clawontwitch', '#esl_csgo', '#ggria', '#amouranth'],

    # if set to true will display any data received
    'debug': False,

    # if set to true will log all messages from all channels
    # todo
    'log_messages': True,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 1024,

    # kafka configuration - for multiple kafka hosts use comma separated values
    'kafka_config': ['localhost:9092'],

    # Settings for app

}