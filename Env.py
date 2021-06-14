from py_telegram_bot_api_framework.SimpleFileStorage import SimpleFileStorage

from BotUser import BotUser
from CameraConfig import CameraConfig
from EventDispatcher import EventDispatcher


class Env(EventDispatcher):
	def __init__(self, **kwargs):
		EventDispatcher.__init__(self)
		self.camera_storage = SimpleFileStorage("data/cameras.json")
		self.user_storage = SimpleFileStorage("data/users.json")

	def get_user(self, tid) -> BotUser:
		default = {"tid": tid}
		return self.user_storage.get(str(tid), default)

	def get_camera_config(self, tid, name) -> CameraConfig:
		key = f'{tid}_{name}'
		return self.camera_storage.get(key)

	def store_user(self, user: BotUser) -> None:
		self.user_storage.set(str(user.id), user.dump())

	def store_camera_config(self, config: CameraConfig) -> None:
		key = f'{config.user}_{config.name}'
		self.camera_storage.set(key, config.dump())

	def add_active_camera(self, tid, name):
		_all = set(self.camera_storage.get("active_camera", []))
		key = f'{tid}_{name}'
		_all.add(key)
		self.camera_storage.set("active_camera", list(_all))

	def remove_active_camera(self, tid, name):
		_all = set(self.camera_storage.get("active_camera", []))
		key = f'{tid}_{name}'
		_all.remove(key)
		self.camera_storage.set("active_camera", list(_all))

	def get_active_camera_list(self):
		_all = set(self.camera_storage.get("active_camera", []))
		return (self.camera_storage.get(key) for key in _all)
