import logging
import time
import urllib.request
from threading import Thread

import cv2
import requests

from EventDispatcher import EventDispatcher
from ONVIFController import ONVIFController
from Storage import CameraConfig
from utils import get_uri, get_uri2


def save_image(uri, path) -> str:
	cap = cv2.VideoCapture(uri)
	# ret, frame = cap.read()
	cap.read()
	if cap.isOpened():
		state, frame = cap.read()
		cap.release()  # releasing camera immediately after capturing picture
		if state and frame is not None:
			cv2.imwrite(path, frame)
			return path
	return ""


def save_video(uri, path, stop_function, codec: str = 'MJPG', frame_rate: int = 15, ):
	# Create a VideoCapture object
	capture = cv2.VideoCapture(uri)
	# Default resolutions of the frame are obtained (system dependent)
	frame_width = int(capture.get(3))
	frame_height = int(capture.get(4))

	# Set up codec and output video settings
	# https://docs.opencv.org/master/dd/d43/tutorial_py_video_display.html
	_codec = cv2.VideoWriter_fourcc(*codec)
	output_video = cv2.VideoWriter(
		path,
		_codec,
		frame_rate,
		(frame_width, frame_height)
	)

	while not stop_function():
		if capture.isOpened():
			status, frame = capture.read()
			output_video.write(frame)

	capture.release()
	output_video.release()


class Action(object):
	def __init__(self, env: EventDispatcher, event_name: str):
		self.env = env
		self.event_name = event_name

		self.chat_id = None
		self.message = None

	def set_params(self, chat_id=None, message=None):
		self.chat_id = chat_id
		self.message = message
		return self

	def do_action(self):
		logging.info(f'Send action event: {self.event_name}')
		self.env.dispatch(self.event_name, self)


class CaptureVideoAction(Action):
	def __init__(self, env: EventDispatcher, event_name: str):
		Action.__init__(self, env, event_name)
		self.uri = None
		self.path = None

		self.__capture = None
		self.__output_video = None
		self.__thread = None
		self.__stop = False

	def start_capture(
			self, uri: str,
			path: str = "output", ext: str = "avi", codec: str = 'MJPG',
			frame_rate: int = 15
	):
		self.uri = uri
		self.path = f'{path}.{ext}'

		# Start the thread to read frames from the video stream
		self.__thread = Thread(target=self.__run, args=())
		self.__thread.daemon = True
		self.__thread.start()
		return self

	def __run(self):
		save_video(self.uri, self.path, self._stop_function)
		self.__thread = None
		logging.info("video capture done")
		self.do_action()

	def _stop_function(self):
		return self.__stop

	def stop(self):
		self.__stop = True


class CaptureVideoLimitedAction(CaptureVideoAction):

	def __init__(self, env: EventDispatcher, event_name: str, duration: int):
		self.start_time = time.time()
		self.duration = duration
		super().__init__(env, event_name)

	def _stop_function(self):
		duration = time.time() - self.start_time
		logging.info(f"frame {duration}")
		return duration > self.duration


class SnapshotAction(Action):
	def __init__(self, env: EventDispatcher, event_name: str):
		super().__init__(env, event_name)
		self.path = None

	def start(self, path, config: CameraConfig, controller: ONVIFController):
		self.path = path

		if controller.can_snapshot():
			uri = controller.get_snapshot_uri().Uri
			uri2 = get_uri2(config, uri, config.onvif_port)
			response = requests.get(uri2)
			with open(path, "wb") as f:
				f.write(response.content)
		else:
			uri = get_uri(config, controller.get_stream_uri())
			save_image(uri, path)

		self.do_action()
		return self


class UploadVideo(Action):
	def __init__(self, env: EventDispatcher, event_name: str):
		super().__init__(env, event_name)

	def start(self, path):
		self.path = path
