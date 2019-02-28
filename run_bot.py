from src.twitchbot.message_producer_processed import TwitchBot as ProcessedProducer
from src.twitchbot.message_producer_raw import RawBot as RawProducer
from src.config.conf import *

ProcessedProducer(config, "twitch-parsed-message").run()
# ProcessedProducer(config, "twitch-parsed-message")
# RawProducer(config, "twitch-raw-message")

