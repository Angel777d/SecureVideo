class EventDispatcher:
	def __init__(self):
		self.__handlers = {}

	def add_event_listener(self, event_name, callback):
		callback_collection = self.__handlers.setdefault(event_name, set())
		callback_collection.add(callback)

	def remove_event_listener(self, event_name, callback):
		callback_collection = self.__handlers.setdefault(event_name, set())
		callback_collection.remove(callback)

	def dispatch(self, event_name, data):
		callback_collection = self.__handlers.setdefault(event_name, set())
		for callback in callback_collection:
			callback(data)
