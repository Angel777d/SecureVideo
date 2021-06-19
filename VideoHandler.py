import logging

from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, MessageBuilder, MessageEntityType, InputFile

from Storage import CameraConfig
from Env import Env
from Actions import CaptureVideoLimitedAction, CaptureVideoAction
from utils import file_time, get_camera_config_from_message, get_uri


class VideoHandler(BotBasicHandler):
	def __init__(self, api: API, config: dict):
		super().__init__(api, config)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	@property
	def api(self) -> API:
		return self.telegram_api

	def _on_initialise(self):
		self.register_command("/video", self.get_video)
		self.env.add_event_listener("media.video", self.on_video)

	def get_video(self, update: Update) -> bool:
		config = get_camera_config_from_message(self.env, update.message)
		if not config:
			logging.warning(f"get_video -- no camera to get video from")
			return True

		controller = self.env.controllers.get(config)
		uri = get_uri(config, controller)

		v, e = MessageBuilder().append("Stream url:\n").append(uri, MessageEntityType.URL).get()
		self.api.send_message(update.message.chat.id, v, entities=e)

		path = f'tmp/{file_time()}'
		ext = self.config.get("ext")
		codec = self.config.get("codec")
		duration = 3

		caption = f"Video: {path}.{ext}"
		CaptureVideoLimitedAction(self.env, "media.video", duration).set_params(
			chat_id=update.message.chat.id,
			message=caption
		).start_capture(uri, path, ext, codec)

		return True

	def on_video(self, action: CaptureVideoAction):
		try:
			self.api.send_document(
				action.chat_id,
				InputFile(action.path),
				caption=f'Video: {action.path}'
			)
		except ValueError as err:
			logging.info(f"Can't send video: {err}")
