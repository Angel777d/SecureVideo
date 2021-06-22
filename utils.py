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


def get_uri(config, uri):
	uri = uri.Uri
	return get_uri2(config, uri, config.rtsp_port)

def get_uri2(config, uri, target_port, useCredentials=True):
	data = uri.split("/")
	protocol = data[0]
	addr = data[2].split(":")
	host = addr[0]
	port = addr[1] if len(addr) > 1 else ""
	path = "/".join(data[3:])
	print("utils", "get_uri", protocol, host, port, path)
	if useCredentials and config.login:
		return f"{protocol}//{config.login}:{config.password}@{config.host}:{target_port}/{path}"
	else:
		return f"{protocol}//{config.host}:{target_port}/{path}"
