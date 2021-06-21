import logging
import time

from Storage import CameraConfig
from Env import Env
from utils import get_uri

RECONNECT_TIMOUT = 60
ALERT_TIMOUT = 30
PULL_TIMEOUT = 1


class DT:
	def __init__(self):
		self.__lastTime = time.time()
		self.__wait_time = 0
		self.__pass_time = 0

	def set_wait_time(self, value):
		self.__wait_time = value

	@property
	def dt(self):
		new_time = time.time()
		result = new_time - self.__lastTime
		self.__lastTime = new_time
		return result

	def process(self):
		self.__pass_time += self.dt
		if self.__wait_time > self.__pass_time:
			return
		self.__pass_time = 0
		self.do_job()

	def do_job(self):
		pass


class AlertData:
	def __init__(self, alert_id, tid, name, uri):
		self.alert_id = alert_id
		self.tid = tid
		self.name = name
		self.uri = uri

	def key(self):
		return self.alert_id, self.tid, self.name


class CameraAlert:
	def __init__(self, env: Env, config: CameraConfig):
		self.env: Env = env
		self.config: CameraConfig = config

		self.inProgress = False
		self.stream_uri = None
		self.timeStarted = 0

		self.alert_id = 0

	def on_motion(self, messages):
		curr_time = time.time()
		if len(messages):
			# print("Alert updated!")
			self.timeStarted = curr_time

		if self.inProgress and curr_time - self.timeStarted > ALERT_TIMOUT:
			logging.info(f'Alert stop. Camera name: {self.config.name}, user: {self.config.tid}')
			data = AlertData(self.alert_id, self.config.tid, self.config.name, self.stream_uri)
			self.inProgress = False
			self.timeStarted = 0
			self.stream_uri = None
			self.env.dispatch("alert.stop", data)
			return

		if not self.inProgress and self.timeStarted:
			logging.info(f'Alert start! Camera name: {self.config.name}, user: {self.config.tid}')
			alert_id = self.alert_id
			self.alert_id += 1
			self.inProgress = True
			controller = self.env.controllers.get(self.config)
			self.stream_uri = get_uri(self.config, controller)
			data = AlertData(alert_id, self.config.tid, self.config.name, self.stream_uri)
			self.env.dispatch("alert.start", data)
			return


class CameraEventsHandler(DT):
	def __init__(self, env: Env, config: CameraConfig):
		DT.__init__(self)
		self.env = env
		self.__config = config
		self.__alert = CameraAlert(env, config)

	@property
	def camera(self):
		if not self.env.controllers.has(self.__config):
			self.set_wait_time(PULL_TIMEOUT)
		return self.env.controllers.get(self.__config)

	def reset_camera(self):
		self.env.controllers.remove(self.__config)
		self.set_wait_time(RECONNECT_TIMOUT)

	def do_job(self):
		try:
			self.camera.request_messages()
			self.__alert.on_motion(self.camera.pull_messages())
		except Exception as ex:
			self.reset_camera()
			logging.info(f'Get messages from camera failed. Recreate camera object. {ex}')


class ActiveCameraPool:
	def __init__(self, env: Env):
		self.env: Env = env
		env.add_event_listener("camera.activate", self.__on_camera_activate)
		env.add_event_listener("camera.deactivate", self.__on_camera_deactivate)
		self.__handlers = {}

	def __on_camera_activate(self, data: CameraConfig):
		self.add_active_camera(data)

	def __on_camera_deactivate(self, data):
		self.remove_active_camera(data)

	def remove_active_camera(self, config: CameraConfig):
		key = config.tid, config.name
		if key in self.__handlers:
			del self.__handlers[key]
			logging.info(f"Deactivate camera: {config.name}")

	def add_active_camera(self, config: CameraConfig):
		key = config.tid, config.name
		print("add_active_camera", config.name)
		if key in self.__handlers:
			print("already active!", config.name)
			return

		logging.info(f"Activate camera: {config.name}")
		self.__handlers[key] = CameraEventsHandler(self.env, config)

	def process(self):
		h = self.__handlers.copy()
		for c in h.values():
			c.process()
