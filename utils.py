from datetime import datetime

from telegram_bot_api import Message

from BotUser import BotUser
from Env import Env


def file_time():
	return datetime.now().strftime("%d%m%Y_%H%M%S")


def get_camera_name_from_message(msg: Message, default: str = ""):
	values = msg.text.split(" ")
	if len(values) > 1:
		return values[-1]
	return default


def get_camera_config_from_message(env: Env, msg: Message):
	tid: int = msg.from_user.id
	user = BotUser.restore(env.get_user(tid))
	name = get_camera_name_from_message(msg, user.default_camera)
	config = env.get_camera_config(tid, name)
	return config
