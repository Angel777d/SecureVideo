class BotUser:
	def __init__(self, tid, cameras=(), default_camera=""):
		self.id = int(tid)
		self.cameras = set(cameras)
		self.default_camera = default_camera

	def add_camera(self, name):
		self.cameras.add(name)
		if not self.default_camera:
			self.default_camera = name

	@classmethod
	def restore(cls, data):
		return cls(**data)

	def dump(self):
		return {
			"tid": self.id,
			"cameras": list(self.cameras),
			"default_camera": self.default_camera,
		}