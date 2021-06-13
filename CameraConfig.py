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

	def format_uri(self, protocol, address, port, path):
		if self.login:
			return f"{protocol}//{self.login}:{self.password}@{self.host}:{self.rtsp_port}/{path}"
		else:
			return f"{protocol}//{self.host}:{self.rtsp_port}/{path}"
