import logging
from typing import Generator

from py_telegram_bot_api_framework.AHandler import AHandler
from telegram_bot_api import API, Update

from Env import Env


class UserDialogHandler(AHandler):
	def __init__(self, api: API, config: dict):
		super().__init__(api, config)
		self.env: Env = config.get("env")

		self.dialogs = {}
		self.env.add_event_listener("dialog.add_user_dialog", self.__on_add_user_dialog)
		self.env.add_event_listener("dialog.remove_user_dialog", self.__on_remove_user_dialog)

	def handle(self, update: Update) -> bool:
		msg = update.message
		if not msg:
			return False

		tid = msg.from_user.id
		if tid not in self.dialogs:
			return False

		dialog: Generator = self.dialogs[tid]
		try:
			dialog.send(msg)
			return True
		except StopIteration:
			logging.info("Dialog error: can't continue. Dialog removed")
			self.dialogs.pop(tid)
			return True

	def __on_add_user_dialog(self, tid, dialog):
		print("dialog added", tid, dialog)
		self.dialogs[tid] = dialog

	def __on_remove_user_dialog(self, tid):
		dialog = self.dialogs.pop(tid)
		print("removed added", tid, dialog)
