from sys import argv
from src.twitchbot.producerbot import ProducerBot
from src.configuration.conf import *
from src.python_aggregator.aggregatorbot import ReaderBot

# kafka_bot = ProducerBot(configuration).run()
counter_bot = ReaderBot(config).run()