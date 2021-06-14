import logging
import time
from threading import Thread

import cv2
from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, MessageBuilder, MessageEntityType, InputFile

from CameraConfig import CameraConfig
from Env import Env
from utils import file_time, get_camera_config_from_message


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

	def get_video(self, update: Update) -> bool:
		config = get_camera_config_from_message(self.env, update.message)
		if not config:
			logging.warning(f"get_video -- no camera to get video from")
			return True

		uri = CameraConfig.restore(config).get_uri()
		v, e = MessageBuilder().append("Stream url: ").append(uri, MessageEntityType.URL).get()
		self.api.send_message(update.message.chat.id, v, entities=e)

		video_path = f'tmp/{file_time()}.avi'
		VideoWriter(uri, 10, video_path, lambda: self.on_video(update.message.chat.id, video_path))
		logging.info(f"get_video END")
		return True

	def on_video(self, chat_id, path):
		self.api.send_document(chat_id, InputFile(path), caption=f'Video: {path}')


class VideoWriter(object):
	def __init__(
			self,
			src: str,
			duration: int,
			path: str = "output.avi",
			callback=None,
			frame_rate: int = 15):
		self.duration = duration
		self.callback = callback

		# Create a VideoCapture object
		self.capture = cv2.VideoCapture(src)
		# Default resolutions of the frame are obtained (system dependent)
		self.frame_width = int(self.capture.get(3))
		self.frame_height = int(self.capture.get(4))

		# Set up codec and output video settings
		self.codec = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
		self.output_video = cv2.VideoWriter(path, self.codec, frame_rate, (self.frame_width, self.frame_height))

		# Start the thread to read frames from the video stream
		self.thread = Thread(target=self.update, args=())
		self.thread.daemon = True
		self.thread.start()

	def update(self):
		start_time = 0
		# Read the next frame from the stream in a different thread
		while True:
			if self.capture.isOpened():
				if not start_time:
					start_time = time.time()
				status, frame = self.capture.read()
				self.output_video.write(frame)

			duration = time.time() - start_time
			logging.info(f"frame {duration}")

			if duration > self.duration:
				break

		self.capture.release()
		self.output_video.release()
		logging.info("video capture done")

		if self.callback:
			self.callback()
