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
		self.register_command("/edit_camera", self.edit_camera)

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
		if not user.default_camera:
			user.default_camera = config.name
			s.store_user(user)

		self.api.send_message(update.message.chat.id, "New camera added!")
		return True

	def edit_camera(self, update: Update) -> bool:
		tid = update.message.from_user.id
		f = self.edit_camera_dialog(update.message)
		self.env.dispatch("dialog.add_user_dialog", tid=tid, dialog=f)
		next(f)
		return True

	def edit_camera_dialog(self, msg):
		tid = msg.from_user.id
		msg = yield self.__on_edit_camera_dialod(tid, "Name of camera pls.")

		name = msg.text
		config = self.env.storage.get_camera_config(tid, name)
		if config:
			msg = yield self.__on_edit_camera_dialod(tid,
													 f"camera [{config.name}]: {config.host}:{config.onvif_port}, isActive: {config.isActive}")
		else:
			self.env.dispatch("dialog.remove_user_dialog", tid)
			yield self.__on_edit_camera_dialod(tid, f"Can't find camera {name}")

		self.env.dispatch("dialog.remove_user_dialog", tid)
		yield self.__on_edit_camera_dialod(tid, f"cant do this yet: {msg.text}")

	def __on_edit_camera_dialod(self, tid, text):
		self.api.send_message(tid, text)
