import logging

import logging_setup

logging_setup.configure("logs", "SecureVideoBot")
from SecureVideoBot import SecureVideoBot
from config import BOT_TOKEN

logging.debug("\n\nstart.py -- SecureVideoBot new start ")

botConfig = {}
bot = SecureVideoBot(BOT_TOKEN, "SecureVideoBot", **botConfig)

bot.start_pooling(update_time=3)
