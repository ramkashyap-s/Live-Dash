from sys import argv
from src.twitchbot.bot import TwitchBot
from src.config.conf import *

my_bot = TwitchBot(config).run()