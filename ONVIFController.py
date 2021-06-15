import logging
from datetime import timedelta

from onvif import ONVIFCamera

from CameraConfig import CameraConfig


class ONVIFController:
	def __init__(self, config):
		logging.info(f"new ONVIFController: {config.host}:{config.onvif_port}")
		camera = ONVIFCamera(config.host, config.onvif_port, config.login, config.password
							 )
		self.__camera = camera
		self.__media = camera.create_media_service()
		self.__messages = []

	def __get_service(self, service_name):
		c = self.__camera
		if service_name in c.services:
			return getattr(c, service_name)
		return getattr(c, f'create_{service_name}_service')()

	@property
	def media(self):
		return self.__get_service("media")

	@property
	def events(self):
		return self.__get_service("events")

	@property
	def pullpoint(self):
		return self.__get_service("pullpoint")

	def request_messages(self):
		events = self.events
		c = events.GetServiceCapabilities()
		if c.WSPullPointSupport:
			messages = self.pullpoint.PullMessages({"MessageLimit": 10, "Timeout": timedelta(seconds=2)})
			self.__on_messages(messages)

	def __on_messages(self, resp):
		if resp.NotificationMessage:
			self.__messages.append(resp)

	def pull_messages(self):
		result = self.__messages
		self.__messages = []
		return result

	def get_stream_uri(self, protocol="RTSP"):
		media = self.__media
		profiles = media.GetProfiles()
		profile_token = profiles[0].token
		uri = media.GetStreamUri({
			"StreamSetup": {
				"Stream": "RTP-Unicast",
				"Transport": {"Protocol": protocol}
			},
			"ProfileToken": profile_token
		})

		data = uri.Uri.split("/")
		protocol = data[0]
		host = data[2].split(":")[0]
		port = data[2].split(":")[1]
		path = "/".join(data[3:])
		return protocol, host, port, path


class ONVIFControllerCollection:
	def __init__(self):
		self.__all = {}

	@staticmethod
	def key(config: CameraConfig):
		return config.user, config.name

	def has(self, config: CameraConfig):
		return self.key(config) in self.__all

	def get(self, config: CameraConfig):
		if not self.has(config):
			return self.add(config)
		return self.__all[self.key(config)]

	def add(self, config: CameraConfig):
		controller = ONVIFController(config)
		self.__all[self.key(config)] = controller
		return controller

	def remove(self, config: CameraConfig):
		self.__all.pop(self.key(config))