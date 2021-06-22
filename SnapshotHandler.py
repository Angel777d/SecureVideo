import logging

from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, InputFile

from Storage import CameraConfig
from Env import Env
from Actions import SnapshotAction, Action
from utils import file_time, get_camera_config_from_message, get_uri


class SnapshotHandler(BotBasicHandler):
	def __init__(self, api: API, config: dict):
		super().__init__(api, config)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	@property
	def api(self) -> API:
		return self.telegram_api

	def _on_initialise(self):
		self.register_command("/snapshot", self.get_snapshot)
		self.env.add_event_listener("media.snapshot", self.on_snapshot)

	def get_snapshot(self, update: Update) -> bool:
		chat_id = update.message.chat.id
		config = get_camera_config_from_message(self.env, update.message)
		controller = self.env.controllers.get(config)
		path = f'tmp/{file_time()}.jpg'
		caption = f"Snapshot: {path}."
		SnapshotAction(self.env, "media.snapshot").set_params(
			chat_id=chat_id,
			message=caption
		).start(path, config, controller)
		return True

	def on_snapshot(self, snapshot: SnapshotAction):
		self.api.send_photo(
			snapshot.chat_id,
			InputFile(snapshot.path),
			caption=snapshot.message
		)
