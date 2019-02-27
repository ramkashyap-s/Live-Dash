from src.configuration.conf import *
from src.python_aggregator.aggregatorbot import ReaderBot

counter_bot = ReaderBot(config).run()