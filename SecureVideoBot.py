import logging
import time
from datetime import datetime
from threading import Thread

import cv2
from py_telegram_bot_api_framework.ABot import ABot
from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from py_telegram_bot_api_framework.SimpleFileStorage import SimpleFileStorage
from telegram_bot_api import Update, InputFile, Message

from BotUser import BotUser
from Camera import Camera
from CameraConfig import CameraConfig


# add_camera - Add camera configuaration
# video - get video from camera
# snapshot - get snapshot from camera

class SecureVideoBot(ABot):
	def __init__(self, token: str, name: str = "DefaultBotName", **kwargs):
		super().__init__(token, name, **kwargs)
		self.camera_storage = SimpleFileStorage("data/cameras.json")
		self.user_storage = SimpleFileStorage("data/users.json")

	def _on_initialise(self):
		print(self.name, "init")
		handler = BotBasicHandler(self.api, self.config)
		handler.register_command("/add_camera", self.add_camera)
		handler.register_command("/video", self.get_video)
		handler.register_command("/snapshot", self.get_snapshot)
		self.handlers.append(handler)

	def __get_user(self, tid) -> BotUser:
		default = {"tid": tid}
		return self.user_storage.get(str(tid), default)

	def __store_user(self, user: BotUser) -> None:
		self.user_storage.set(str(user.id), user.dump())

	def __get_camera_config(self, tid, name) -> CameraConfig:
		key = f'{tid}_{name}'
		return self.camera_storage.get(key)

	def __store_camera_config(self, config: CameraConfig) -> None:
		key = f'{config.user}_{config.name}'
		self.camera_storage.set(key, config.dump())

	@staticmethod
	def __camera_config_from_message(tid: int, msg: Message):
		params = msg.text.split(" ")[1:]
		params = {i.split("=")[0]: i.split("=")[1] for i in params}
		params["user"] = tid
		config = CameraConfig(**params)
		return config

	@staticmethod
	def __get_camera_name_from_message(msg: Message, default: str = ""):
		values = msg.text.split(" ")
		if len(values) > 1:
			return values[-1]
		return default

	def add_camera(self, update: Update) -> bool:
		logging.info(f"add_camera --  user: {update.message.from_user}, message:{update.message.text}")

		tid: int = update.message.from_user.id

		config = self.__camera_config_from_message(tid, update.message)
		self.__store_camera_config(config)

		user = BotUser.restore(self.__get_user(tid))
		user.add_camera(config.name)
		self.__store_user(user)

		self.api.send_message(update.message.chat.id, "New camera added!")
		return True

	def get_snapshot(self, update: Update) -> bool:
		pass

	def get_video(self, update: Update) -> bool:
		tid: int = update.message.from_user.id
		user = BotUser.restore(self.__get_user(tid))
		name = self.__get_camera_name_from_message(update.message, user.default_camera)
		config = self.__get_camera_config(tid, name)

		if not config:
			logging.warning(f"get_video -- no camera to get video from")
			return True

		config = CameraConfig.restore(config)
		camera = Camera(config.host, config.onvif_port, config.login, config.password)
		protocol, address, port, path = camera.get_stream_uri()
		uri = config.format_uri(protocol, address, port, path)

		logging.info(f"get_video -- uri: {uri}")
		self.api.send_message(update.message.chat.id, f"video url: {uri}")

		video_path = f'video/{datetime.now().strftime("%d_%m_%Y_%H_%M_%S")}.avi'
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

# EOF
