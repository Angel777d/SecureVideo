import logging
import time

from CameraConfig import CameraConfig
from EventDispatcher import EventDispatcher
from ONVIFController import ONVIFController


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
	def __init__(self, alert_id, user, name, uri):
		self.alert_id = alert_id
		self.user = user
		self.name = name
		self.uri = uri

	def key(self):
		return self.alert_id, self.user, self.name


class CameraAlert:
	def __init__(self, env: EventDispatcher, config: CameraConfig):
		self.env: EventDispatcher = env
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

		if self.inProgress and curr_time - self.timeStarted > 30:
			logging.info(f'Alert stop. Camera name: {self.config.name}, user: {self.config.user}')
			data = AlertData(self.alert_id, self.config.user, self.config.name, self.stream_uri)
			self.env.dispatch("alert.stop", data)
			self.inProgress = False
			self.timeStarted = 0
			self.stream_uri = None
			return

		if not self.inProgress and self.timeStarted:
			logging.info(f'Alert start! Camera name: {self.config.name}, user: {self.config.user}')
			self.alert_id += 1
			self.inProgress = True
			self.stream_uri = self.config.get_uri()
			data = AlertData(self.alert_id, self.config.user, self.config.name, self.stream_uri)
			self.env.dispatch("alert.start", data)
			return


class CameraEventsHandler(DT):
	def __init__(self, env: EventDispatcher, config: CameraConfig):
		DT.__init__(self)

		self.__config = config
		self.__camera: ONVIFController = self.__create_camera_function(config)

		self.__alert = CameraAlert(env, config)

	@staticmethod
	def __create_camera_function(config: CameraConfig) -> ONVIFController:
		return ONVIFController(config.host, config.onvif_port, config.login, config.password)

	@property
	def camera(self):
		if not self.__camera:
			self.__camera = self.__create_camera_function(self.__config)
			self.set_wait_time(10)
		return self.__camera

	def reset_camera(self):
		self.__camera = None
		self.set_wait_time(60)

	def do_job(self):
		try:
			self.camera.request_messages()
			self.__alert.on_motion(self.camera.pull_messages())
		except Exception as ex:
			self.reset_camera()
			logging.info(f'Get messages from camera failed. Recreate camera object. {ex}')


class ActiveCameraPool:
	def __init__(self, env: EventDispatcher):
		self.env: EventDispatcher = env
		env.add_event_listener("camera.activate", self.__on_camera_activate)
		env.add_event_listener("camera.deactivate", self.__on_camera_deactivate)
		self.__handlers = {}

	def __on_camera_activate(self, data: CameraConfig):
		self.add_active_camera(data)

	def __on_camera_deactivate(self, data):
		self.remove_active_camera(data)

	def remove_active_camera(self, config: CameraConfig):
		key = config.user, config.name
		if key in self.__handlers:
			del self.__handlers[key]

	def add_active_camera(self, config: CameraConfig):
		key = config.user, config.name
		print("add_active_camera", config.name)
		if key in self.__handlers:
			print("already active!", config.name)
			return

		logging.info(f"Activate camera: {config.name}")
		self.__handlers[key] = CameraEventsHandler(self.env, config)

	def process(self):
		for c in self.__handlers.values():
			c.process()
