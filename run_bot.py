from src.twitchbot.message_producer_processed import TwitchBot as ProcessedProducer
from src.twitchbot.message_producer_raw import RawBot as RawProducer
from src.config.conf import *

parsed_producer = ProcessedProducer(config, "twitch-parsed-message").run()
#raw_producer = RawProducer(config, "twitch-raw-message").run()

