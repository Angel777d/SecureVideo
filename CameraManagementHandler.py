import logging

from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, Message

from Storage import CameraConfig, BotUser
from Env import Env


class CameraManagementHandler(BotBasicHandler):
	def __init__(self, api: API, config: dict):
		super().__init__(api, config)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	@property
	def api(self) -> API:
		return self.telegram_api

	def _on_initialise(self):
		self.register_command("/add_camera", self.add_camera)

	@staticmethod
	def __camera_config_from_message(tid: int, msg: Message):
		params = msg.text.split(" ")[1:]
		params = {i.split("=")[0]: i.split("=")[1] for i in params}
		params["tid"] = tid
		config = CameraConfig(**params)
		return config

	def add_camera(self, update: Update) -> bool:
		logging.info(f"add_camera --  user: {update.message.from_user}, message:{update.message.text}")

		tid: int = update.message.from_user.id

		config = self.__camera_config_from_message(tid, update.message)
		s = self.env.storage
		s.store_camera_config(config)
		s.add_active_camera(tid, config.name)
		self.env.dispatch("camera.activate", config)

		user = s.get_user(tid)
		user.add_camera(config.name)
		s.store_user(user)

		self.api.send_message(update.message.chat.id, "New camera added!")
		return True
