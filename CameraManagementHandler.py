import logging

from py_telegram_bot_api_framework.BotBasicHandler import BotBasicHandler
from telegram_bot_api import API, Update, Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, \
	ForceReply, utils, MessageBuilder, MessageEntityType, CallbackQuery, InputFile, InputMediaPhoto

from Actions import save_image
from Storage import CameraConfig, BotUser, public_vars
from Env import Env
from utils import get_uri, file_time


class CameraManagementHandler(BotBasicHandler):
	def __init__(self, api: API, config: dict):
		super().__init__(api, config)

	@property
	def env(self) -> Env:
		return self.config.get("env")

	@property
	def api(self) -> API:
		return self.telegram_api

	def _on_initialise(self):
		self.register_command("/cameras", self.camera_control)

	@staticmethod
	def __camera_config_from_message(tid: int, msg: Message):
		params = msg.text.split(" ")[1:]
		params = {i.split("=")[0]: i.split("=")[1] for i in params}
		params["tid"] = tid
		config = CameraConfig(**params)
		return config

	def camera_control(self, update: Update) -> bool:
		chat_id = update.message.chat.id
		tid = update.message.from_user.id

		cams = self.env.storage.get_user_camera(tid)
		keys = [[InlineKeyboardButton(
			text=config.name,
			callback_data=f"camera_edit:{config.name}:i"  # info
		)] for config in cams]
		keys = InlineKeyboardMarkup([[InlineKeyboardButton(text="Add ...", callback_data="camera_add")]] + keys)

		text = f"Camera controls: total ({len(cams)})"
		self.api.send_message(chat_id, text, reply_markup=keys)
		return True

	def handle_callback(self, update: Update) -> bool:
		callback_data: str = update.callback_query.data
		tid = update.callback_query.from_user.id

		if callback_data == "camera_add":
			self.api.answer_callback_query(update.callback_query.id)
			self.__start_dialog(tid, self.add_camera_dialog(tid))
			return True

		if callback_data.startswith("camera_edit"):
			_, name, action = callback_data.split(":")
			config = self.env.storage.get_camera_config(tid, name)

			if action == "i":  # info
				# self.api.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
				text, entities = self.__get_camera_info(config)
				self.api.send_message(tid, text, entities=entities, reply_markup=self.__get_camera_keys(config))
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "p":  # camera params
				text = f'Edit "{config.name}" params:'
				# self.api.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
				self.api.send_message(tid, text, reply_markup=self.__get_params_keys(config))
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "c":  # camera credentials
				# self.api.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
				self.__start_dialog(tid, self.edit_camera_credentials_dialog(tid, name))
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "o":  # camera options
				text = f'Edit "{config.name}" options:'
				self.api.send_message(tid, text, reply_markup=self.__get_options_keys(config))
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "o_img":
				config.alert_send_image = not config.alert_send_image
				self.__update_options(config, update.callback_query)
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "o_vid":
				config.alert_send_video = not config.alert_send_video
				self.__update_options(config, update.callback_query)
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "o_cloud":
				config.alert_cloud_video = not config.alert_cloud_video
				self.__update_options(config, update.callback_query)
				self.api.answer_callback_query(update.callback_query.id)
			elif action == "a":  # camera activate
				config.isActive = not config.isActive
				self.env.storage.store_camera_config(config)
				self.env.dispatch("camera.activate" if config.isActive else "camera.deactivate", config)

				text = f'Camera "{config.name} {"Activated" if config.isActive else "Deactivated"}"'
				self.api.answer_callback_query(update.callback_query.id, text)

				text, entities = self.__get_camera_info(config)
				m = update.callback_query.message
				self.api.edit_message_text(m.chat.id, m.message_id, text=text, entities=entities)
				self.api.edit_message_reply_markup(m.chat.id, m.message_id, reply_markup=self.__get_camera_keys(config))
			else:
				self.__start_dialog(tid, self.edit_camera_property_dialog(tid, name, action))
				self.api.answer_callback_query(update.callback_query.id)
			return True

		if callback_data.startswith("camera_remove"):
			_, name = callback_data.split(":")
			config = self.env.storage.get_camera_config(tid, name)
			self.env.dispatch("camera.deactivate", config)
			self.env.storage.remove_camera(tid, name)
			text = f'Camera "{name}" removed!'
			self.api.answer_callback_query(update.callback_query.id, text=text)
			return True
		if callback_data.startswith("camera_ptz"):
			_, name, action = callback_data.split(":")
			config = self.env.storage.get_camera_config(tid, name)
			controller = self.env.controllers.get(config)
			status = controller.ptz_status()
			print(status.Position.PanTilt.x, status.Position.PanTilt.y)
			if action == "i":
				uri = get_uri(config, controller)
				path = f'tmp/{file_time()}.jpg'
				img_path = save_image(uri, path)
				self.api.answer_callback_query(update.callback_query.id)
				self.api.send_photo(tid, InputFile(img_path), reply_markup=self.__get_ptz_keys(config))
			else:
				dx = dy = 0
				if action == "r":
					dx = 10
				if action == "l":
					dx = -10
				if action == "u":
					dy = 5
				if action == "d":
					dy = -5
				controller.ptz_action(dx, dy)
				uri = get_uri(config, controller)
				path = f'tmp/{file_time()}.jpg'
				img_path = save_image(uri, path)
				self.api.answer_callback_query(update.callback_query.id)

				self.api.send_photo(tid, InputFile(img_path), reply_markup=self.__get_ptz_keys(config))
				self.api.delete_message(
					chat_id=update.callback_query.message.chat.id,
					message_id=update.callback_query.message.message_id,
				)
			return True
		return False

	# messages helpers
	def __update_options(self, config: CameraConfig, callback_query: CallbackQuery):
		self.env.storage.store_camera_config(config)
		self.api.edit_message_reply_markup(
			chat_id=callback_query.message.chat.id,
			message_id=callback_query.message.message_id,
			reply_markup=self.__get_options_keys(config)
		)

	@staticmethod
	def __get_camera_info(config):
		b = MessageBuilder().append(f'Camera "{config.name}" info: \n')
		b.append(f"Host: ", MessageEntityType.BOLD).append(f"{config.host}\n")
		b.append(f"ONVIF: ", MessageEntityType.BOLD).append(f"{config.onvif_port}\n")
		b.append(f"RTSP: ", MessageEntityType.BOLD).append(f"{config.rtsp_port}\n")
		b.append(f"Active: ", MessageEntityType.BOLD).append(f"{config.isActive}\n")
		return b.get()

	@staticmethod
	def __get_camera_keys(config):
		activate_text = "Deactivate" if config.isActive else "Activate"
		return InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(activate_text, callback_data=f'camera_edit:{config.name}:a')],
			[InlineKeyboardButton(text="PTZ", callback_data=f'camera_ptz:{config.name}:i'), ],
			[InlineKeyboardButton(text="Params", callback_data=f'camera_edit:{config.name}:p'), ],
			[InlineKeyboardButton(text="Credentials", callback_data=f'camera_edit:{config.name}:c'), ],
			[InlineKeyboardButton(text="Options", callback_data=f'camera_edit:{config.name}:o'), ],
			[InlineKeyboardButton(text="Remove", callback_data=f'camera_remove:{config.name}'), ],
		])

	@staticmethod
	def __get_ptz_keys(config):
		return InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(text="Up", callback_data=f"camera_ptz:{config.name}:u"), ],
			[
				InlineKeyboardButton(text="Left", callback_data=f"camera_ptz:{config.name}:l"),
				InlineKeyboardButton(text="Right", callback_data=f"camera_ptz:{config.name}:r"),
			],
			[InlineKeyboardButton(text="Down", callback_data=f"camera_ptz:{config.name}:d"), ],
		])

	@staticmethod
	def __get_params_keys(config):
		return InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(f"Edit host", callback_data=f"camera_edit:{config.name}:host")],
			[InlineKeyboardButton(f"Edit ONVIF", callback_data=f"camera_edit:{config.name}:onvif_port")],
			[InlineKeyboardButton(f"Edit RTSP", callback_data=f"camera_edit:{config.name}:rtsp_port")],
		])

	@staticmethod
	def __get_options_keys(config):
		c = config
		return InlineKeyboardMarkup(inline_keyboard=[
			[InlineKeyboardButton(f"Alert image: {c.alert_send_image}", callback_data=f"camera_edit:{c.name}:o_img")],
			[InlineKeyboardButton(f"Alert video: {c.alert_send_video}", callback_data=f"camera_edit:{c.name}:o_vid")],
			[InlineKeyboardButton(
				f"Alert cloud: {c.alert_cloud_video}",
				callback_data=f"camera_edit:{c.name}:o_cloud")],
		])

	# DIALOGS
	def __start_dialog(self, tid, dialog):
		self.env.dispatch("dialog.add_user_dialog", tid=tid, dialog=dialog)
		next(dialog)
		return dialog

	def edit_camera_dialog(self, msg):
		tid = msg.from_user.id
		msg = yield self.api.send_message(tid, "Name of camera pls.")

		name = msg.text
		config = self.env.storage.get_camera_config(tid, name)
		if config:
			msg = yield self.api.send_message(
				tid,
				f"camera [{config.name}]: {config.host}:{config.onvif_port}, isActive: {config.isActive}"
			)
		else:
			self.env.dispatch("dialog.remove_user_dialog", tid)
			yield self.api.send_message(tid, f"Can't find camera {name}")

		self.env.dispatch("dialog.remove_user_dialog", tid)
		yield self.api.send_message(tid, f"cant do this yet: {msg.text}")

	def add_camera_dialog(self, tid):
		msg = yield self.api.send_message(tid, "Camera name:", reply_markup=ForceReply())

		name = msg.text
		config = self.env.storage.get_camera_config(tid, name)

		msg = yield self.api.send_message(tid, "Camera host:", reply_markup=ForceReply())
		host = msg.text

		config.host = host
		self.env.dispatch("dialog.remove_user_dialog", tid)
		self.env.storage.store_camera_config(config)

		text, entities = self.__get_camera_info(config)
		self.api.send_message(tid, text, entities=entities, reply_markup=self.__get_camera_keys(config))
		yield

	def edit_camera_property_dialog(self, tid, name, property_name):
		config = self.env.storage.get_camera_config(tid, name)
		bot_msg = self.api.send_message(tid, f"Enter new {property_name}", reply_markup=ForceReply())
		msg = yield bot_msg
		config.apply_property(property_name, msg.text)
		self.env.storage.store_camera_config(config)
		self.env.dispatch("dialog.remove_user_dialog", tid)
		self.api.send_message(tid, self.__get_camera_info(config))
		yield

	def edit_camera_credentials_dialog(self, tid, name):
		config = self.env.storage.get_camera_config(tid, name)

		bot_msg = self.api.send_message(tid, "Enter login:", reply_markup=ForceReply())
		msg: Message = yield bot_msg
		config.login = msg.text
		# self.api.delete_message(bot_msg.chat.id, bot_msg.message_id)

		bot_msg = self.api.send_message(tid, "Enter password:", reply_markup=ForceReply())
		msg: Message = yield bot_msg
		config.password = msg.text
		# self.api.delete_message(bot_msg.chat.id, bot_msg.message_id)

		self.env.storage.store_camera_config(config)
		self.env.dispatch("dialog.remove_user_dialog", tid)

		text, entities = self.__get_camera_info(config)
		bot_msg = self.api.send_message(tid, text, entities=entities, reply_markup=self.__get_camera_keys(config))
		yield bot_msg
