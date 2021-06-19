from tinydb import TinyDB, Query

_DEFAULT_ONVIF_PORT = 2020
_DEFAULT_RTSP_PORT = 554


def public_vars(obj):
	return {k: getattr(obj, k) for k in vars(obj) if not k.startswith("_")}


class CameraConfig:
	def __init__(
			self, tid: int, name: str,
			host: str = "",
			onvif_port: int = _DEFAULT_ONVIF_PORT,
			rtsp_port: int = _DEFAULT_RTSP_PORT,
			login: str = "",
			password: str = "",
			alert_send_image: bool = True,
			alert_send_video: bool = False,
			alert_cloud_video: bool = True,
			**kwargs
	):
		self.tid = tid
		self.name = name
		self.host = host

		self.onvif_port = int(onvif_port)
		self.rtsp_port = int(rtsp_port)

		self.login = login
		self.password = password

		self.alert_send_image = alert_send_image
		self.alert_send_video = alert_send_video
		self.alert_cloud_video = alert_cloud_video

		self.isActive = True


class BotUser:
	def __init__(self, tid, default_camera="", **kwargs):
		self.tid = int(tid)
		self.default_camera = default_camera


class Storage:
	def __init__(self, storage_path: str = "data", **kwargs):
		self.db = TinyDB(f'{storage_path}/db.json')

	def get_user(self, tid: int) -> BotUser:
		assert tid, "user id is mandatory"
		User = Query()
		table = self.db.table('user')
		result = table.search(User.tid == tid)
		if result:
			return BotUser(**result[0])

		table.insert({"tid": tid})
		return BotUser(tid)

	def get_camera_config(self, tid, name) -> CameraConfig:
		assert tid, "user id is mandatory"
		assert name, "camera name is mandatory"
		Camera = Query()
		table = self.db.table('camera')
		result = table.search((Camera.name == name) & (Camera.tid == tid))
		if result:
			return CameraConfig(**result[0])
		data = {"tid": tid, "name": name}
		table.insert(data)
		return CameraConfig(**data)

	def store_user(self, user: BotUser) -> None:
		User = Query()
		self.db.table('user').update(public_vars(user), User.tid == user.tid)

	def store_camera_config(self, config: CameraConfig) -> None:
		Camera = Query()
		table = self.db.table('camera')
		if not table.contains((Camera.name == config.name) & (Camera.tid == config.tid)):
			table.insert(public_vars(config))
		else:
			table.update(public_vars(config), (Camera.name == config.name) & (Camera.tid == config.tid))

	def add_active_camera(self, tid, name):
		Camera = Query()
		self.db.table('camera').update({"isActive": True}, (Camera.name == name) & (Camera.tid == tid))

	def remove_active_camera(self, tid, name):
		Camera = Query()
		self.db.table('camera').update({"isActive": False}, (Camera.name == name) & (Camera.tid == tid))

	def get_active_camera_list(self):
		Camera = Query()
		return [CameraConfig(**v) for v in self.db.table('camera').search((Camera.isActive == True))]
