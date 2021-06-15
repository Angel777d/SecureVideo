_DEFAULT_ONVIF_PORT = 2020
_DEFAULT_RTSP_PORT = 554


class CameraConfig:
	def __init__(
			self, user, name, host,
			onvif_port=_DEFAULT_ONVIF_PORT,
			rtsp_port=_DEFAULT_RTSP_PORT,
			login=None,
			password=None):

		self.user = user
		self.name = name
		self.host = host
		self.onvif_port = int(onvif_port)
		self.rtsp_port = int(rtsp_port)
		self.login = login
		self.password = password

		self.alert_send_image = True
		self.alert_send_video = False
		self.alert_cloud_video = True

	@classmethod
	def restore(cls, data):
		if not data:
			return None
		if "host" not in data:
			return None
		if "name" not in data:
			return None
		return cls(**data)

	def dump(self) -> dict:
		data = {"user": self.user, "name": self.name, "host": self.host}
		if self.login:
			data.update({"login": self.login})
		if self.password:
			data.update({"password": self.password})
		if self.onvif_port != _DEFAULT_ONVIF_PORT:
			data.update({"onvif_port": self.onvif_port})
		if self.rtsp_port != _DEFAULT_RTSP_PORT:
			data.update({"rtsp_port": self.rtsp_port})
		return data
