import logging
import time
from threading import Thread

import cv2

from EventDispatcher import EventDispatcher


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
		self.path = f'{path}.{ext}'

		# Create a VideoCapture object
		self.__capture = cv2.VideoCapture(uri)
		# Default resolutions of the frame are obtained (system dependent)
		frame_width = int(self.__capture.get(3))
		frame_height = int(self.__capture.get(4))

		# Set up codec and output video settings
		# https://docs.opencv.org/master/dd/d43/tutorial_py_video_display.html
		_codec = cv2.VideoWriter_fourcc(*codec)
		self.__output_video = cv2.VideoWriter(
			self.path,
			_codec,
			frame_rate,
			(frame_width, frame_height)
		)

		# Start the thread to read frames from the video stream
		self.__thread = Thread(target=self.__run, args=())
		self.__thread.daemon = True
		self.__thread.start()
		return self

	def __run(self):
		while True:
			self._do_job()
			if self.__stop:
				break
		self.__finalize()

	def __finalize(self):
		self.__thread = None

		self.__capture.release()
		self.__output_video.release()
		logging.info("video capture done")

		self.do_action()

	def _do_job(self):
		if self.__capture.isOpened():
			status, frame = self.__capture.read()
			self.__output_video.write(frame)

	def stop(self):
		self.__stop = True


class CaptureVideoLimitedAction(CaptureVideoAction):

	def __init__(self, env: EventDispatcher, event_name: str, duration: int):
		self.start_time = time.time()
		self.duration = duration
		super().__init__(env, event_name)

	def _do_job(self):
		super()._do_job()
		duration = time.time() - self.start_time
		logging.info(f"frame {duration}")
		if duration > self.duration:
			self.stop()


class SnapshotAction(Action):
	def __init__(self, env: EventDispatcher, event_name: str):
		super().__init__(env, event_name)
		self.path = None

	def start(self, uri, path):
		self.path = path
		cap = cv2.VideoCapture(uri)
		# ret, frame = cap.read()
		cap.read()
		if cap.isOpened():
			state, frame = cap.read()
			cap.release()  # releasing camera immediately after capturing picture
			if state and frame is not None:
				cv2.imwrite(path, frame)
				self.do_action()
		return self
