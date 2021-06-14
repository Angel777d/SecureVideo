import logging

from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, InputFile

from CameraConfig import CameraConfig
from Env import Env
from MediaWriter import SnapshotAction, Action
from utils import file_time, get_camera_config_from_message


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
		if not config:
			logging.warning(f"get_snapshot -- no camera to get snapshot from")
			return True

		uri = CameraConfig.restore(config).get_uri()
		path = f'tmp/{file_time()}.jpg'

		SnapshotAction(self.env, "media.snapshot").set_params(chat_id=chat_id, path=path, uri=uri).start(uri, path)

	def on_snapshot(self, snapshot: Action):
		self.api.send_photo(
			snapshot.chat_id,
			InputFile(snapshot.path),
			caption=f'{snapshot.path}.jpg'
		)
