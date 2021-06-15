import threading
import time

from py_telegram_bot_api_framework.ABot import ABot

from Actions import SnapshotAction, CaptureVideoAction
from ActiveCameraPool import ActiveCameraPool, AlertData
from BotUser import BotUser
from CameraConfig import CameraConfig
from CameraManagementHandler import CameraManagementHandler
from Env import Env
from SnapshotHandler import SnapshotHandler
from VideoHandler import VideoHandler
from utils import file_time

MAIN_LOOP_SLEEP_TIME = 1


class SecureVideoBot(ABot):
	# add_camera - Add camera configuration
	# video - get video from camera
	# snapshot - get snapshot from camera

	def __init__(self, token: str, name: str = "DefaultBotName", **kwargs):
		env = Env(**kwargs)
		kwargs.update({"env": env})
		self.__main_loop = None
		self.__cameras = ActiveCameraPool(env)
		self.__actions = {}
		super().__init__(token, name, **kwargs)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	def _on_initialise(self):
		self.add_handlers(CameraManagementHandler, VideoHandler, SnapshotHandler)
		self.add_listeners()

		# restore active cameras from storage
		active_cam = self.env.get_active_camera_list()
		for cam in active_cam:
			self.__cameras.add_active_camera(CameraConfig.restore(cam))

		# start main loop
		threading.Thread(target=self.main_loop).start()

	def add_listeners(self):
		self.env.add_event_listener("alert.start", self.__on_alert_start)
		self.env.add_event_listener("alert.stop", self.__on_alert_stop)

	def main_loop(self):
		while True:
			self.__cameras.process()
			time.sleep(MAIN_LOOP_SLEEP_TIME)

	def __on_alert_start(self, alert: AlertData):
		print("start alert key", alert.key())
		uri = alert.uri
		cam = CameraConfig.restore(self.env.get_camera_config(alert.user, alert.name))
		usr = BotUser.restore(self.env.get_user(alert.user))

		if cam.alert_send_image:
			path = f'tmp/{file_time()}.jpg'
			SnapshotAction(self.env, "media.snapshot").set_params(
				chat_id=usr.id,
				message=f"Alert ({alert.alert_id})! Snapshot sent.",
			).start(uri, path)

		if cam.alert_send_video:
			path = f'tmp/{file_time()}'
			ext = self.config.get("ext")
			codec = self.config.get("codec")

			self.__actions[alert.key()] = CaptureVideoAction(self.env, "media.video").set_params(
				chat_id=usr.id,
				message=f'{path}.{ext}'
			).start_capture(uri, path, ext, codec)

	def __on_alert_stop(self, alert: AlertData):
		print("stop alert key", alert.key())
		if alert.key() in self.__actions:
			self.__actions.pop(alert.key()).stop()
