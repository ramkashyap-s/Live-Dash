global config

config = {

    # details required to login to twitch IRC server
    'server': 'irc.twitch.tv',
    'port': 6667,
    'username': 'srk3141', # your twitch username
    'oauth_password': 'oauth:stohe9j4evimw08quy46nm5htphllu',  # get this from http://twitchapps.com/tmi/

    # channel to join '#clawontwitch', #moonmoon_ow, #neuro, #rajjpatel, #disguisedtoast, #somagreen, #macaiyla,
    #trainwreckstv
    'channels': ['ninja','clawontwitch','moonmoon_ow','badbunny', 'amouranth ', 'therealshookon3', 'stephenfra', 'sienne', 'beautiffal'],
    # 'channels' : ['ninja', 'shroud', 'meclipse', 'tsm_myth', 'tfue', 'summit1g', 'riotgames', 'timthetatman', 'dakotaz',
    #               'tsm_daequan', 'drdisrespect', 'drlupo', 'syndicate', 'pokimane', 'esl_csgo', 'esltv_cs', 'imaqtpie',
    #               'nightblue3', 'lirik', 'lirikk', 'sodapoppin', 'loltyler1', 'nickmercs', 'sypherpk', 'cdnthe3rd', 'fortnite',
    #               'castro_1021', 'faker', 'theoriginalweed', 'joshog', 'Faceit', 'faceittv', 'eleaguetv', 'dyrus', 'gosu', 'dreamhackcs',
    #               'wolves_bjergsen', 'tsm_bjergsen', 'officialbjergsen', 'boxbox', 'tsm_hamlinz', 'lolitofdez', 'alanzoka', 'electronicdesire',
    #               'PhantomL0rd', 'goldglove', 'gdq', 'gamesdonequick', 'speeddemosarchivesda', 'sgdq', 'c9sneaky', 'gotaga', 'captainsparklez',
    #               'montanablack88', 'yoda', 'stonedyooda', 'trick2g', 'nl_kripp', 'highdistortion', 'overwatchleague', 'kingrichard',
    #               'doublelift_renamed300203', 'doublelift', 'cizzorz', 'swiftor', 'izakooo', 'couragejd', 'jericho', 'cohhcarnage', 'cohh',
    #               'voyboy', 'bobross', 'sivhd', 'kittyplays', 'kittyplaysgames', 'jahrein', 'sovietwomble', 'thenadeshot', 'nadeshot',
    #               'forsen', 'pewdiepie', 'anomaly', 'ungespielt', 'elded', 'dedreviil2', 'wtcn', 'gronkh', 'grimmmz', 'a_seagull', 'amaz',
    #               'amazhs', 'pashabiceps', 'kinggothalion', 'tsm_theoddone', 'unlostv', 'markiplier', 'anomalyxd', 'disguisedtoast', 'xqcow',
    #               'zeeoon'],
    # if set to true will display any data received
    'debug': False,

    # if set to true will log all messages from all channels
    # todo
    'log_messages': True,

    # maximum amount of bytes to receive from socket - 1024-4096 recommended
    'socket_buffer_size': 1024,

    # kafka config - for multiple kafka hosts use comma separated values
    'kafka_brokers': ['localhost:9092'],

    'kafka_topic' : "twitch-parsed-message"

# Settings for app

}