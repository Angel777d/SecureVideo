import threading
import time

from py_telegram_bot_api_framework.ABot import ABot

from ActiveCameraPool import ActiveCameraPool
from CameraConfig import CameraConfig
from CameraManagementHandler import CameraManagementHandler
from Env import Env
from SnapshotHandler import SnapshotHandler
from VideoHandler import VideoHandler


class SecureVideoBot(ABot):

	def __init__(self, token: str, name: str = "DefaultBotName", **kwargs):
		env = Env(**kwargs)
		kwargs.update({"env": env})
		self.__main_loop = None
		self.__cameras = ActiveCameraPool(env)

		super().__init__(token, name, **kwargs)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	def _on_initialise(self):
		print(self.name, "init")
		# add_camera - Add camera configuaration
		# video - get video from camera
		# snapshot - get snapshot from camera

		self.add_handlers(CameraManagementHandler, VideoHandler, SnapshotHandler)

		active_cam = self.env.get_active_camera_list()

		for cam in active_cam:
			self.__cameras.add_active_camera(CameraConfig.restore(cam))

		threading.Thread(target=self.main_loop).start()

	def main_loop(self):
		while True:
			self.__cameras.process()
			time.sleep(10)
