from py_telegram_bot_api_framework.SimpleFileStorage import SimpleFileStorage

from Storage import CameraConfig, BotUser, Storage
from EventDispatcher import EventDispatcher
from ONVIFController import ONVIFControllerCollection


class Env(EventDispatcher):
	def __init__(self, **kwargs):
		EventDispatcher.__init__(self)
		# self.camera_storage = SimpleFileStorage("data/cameras.json")
		# self.user_storage = SimpleFileStorage("data/users.json")
		self.storage = Storage(**kwargs)
		self.controllers: ONVIFControllerCollection = ONVIFControllerCollection()


