import json
import logging

import logging_setup

logging_setup.configure("logs", "SecureVideoBot")

from SecureVideoBot import SecureVideoBot


if __name__ == '__main__':
	logging.debug("\n\nstart.py -- SecureVideoBot new start ")
	with open("data/config.json") as json_data_file:
		config = json.load(json_data_file)

	bot = SecureVideoBot(**config)
	bot.start_pooling(update_time=3)
