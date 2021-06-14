import logging

import cv2
from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, InputFile

from CameraConfig import CameraConfig
from Env import Env
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

	def get_snapshot(self, update: Update) -> bool:
		chat_id = update.message.chat.id
		config = get_camera_config_from_message(self.env, update.message)
		if not config:
			logging.warning(f"get_snapshot -- no camera to get snapshot from")
			return True

		camera = CameraConfig.restore(config)
		cap = cv2.VideoCapture(camera.get_uri())
		# ret, frame = cap.read()
		cap.read()
		if cap.isOpened():
			state, frame = cap.read()
			cap.release()  # releasing camera immediately after capturing picture
			if state and frame is not None:
				file_name = file_time()
				path = f'tmp/{file_name}.jpg'
				cv2.imwrite(path, frame)

				self.api.send_photo(
					chat_id,
					InputFile(path),
					caption=f'{file_name}.jpg from {camera.name} [{camera.host}]'
				)
