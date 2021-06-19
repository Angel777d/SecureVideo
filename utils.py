from datetime import datetime

from telegram_bot_api import Message

from Storage import BotUser, CameraConfig
from Env import Env


def file_time():
	return datetime.now().strftime("%d%m%Y_%H%M%S")


def get_camera_name_from_message(msg: Message, default: str = ""):
	values = msg.text.split(" ")
	if len(values) > 1:
		return values[-1]
	return default


def get_camera_config_from_message(env: Env, msg: Message) -> CameraConfig:
	tid: int = msg.from_user.id
	user: BotUser = env.storage.get_user(tid)
	name: str = get_camera_name_from_message(msg, user.default_camera)
	config: CameraConfig = env.storage.get_camera_config(tid, name)
	return config


def get_uri(config, controller):
	protocol, address, port, path = controller.get_stream_uri()
	if config.login:
		return f"{protocol}//{config.login}:{config.password}@{config.host}:{config.rtsp_port}/{path}"
	else:
		return f"{protocol}//{config.host}:{config.rtsp_port}/{path}"
