import logging


def configure(log_path, file_name):
	format_default = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
	format_stream = "[%(asctime)s] [%(levelname)s]  %(message)s"
	format_datetime_default = '%y-%m-%d %H:%M:%S'


	logging.basicConfig(
		level=logging.DEBUG,
		format=format_default,
		datefmt=format_datetime_default,
		handlers=[],
	)

	root_logger = logging.getLogger()

	file_handler = logging.FileHandler("{0}/{1}.log".format(log_path, file_name))
	file_handler.setLevel(logging.DEBUG)
	root_logger.addHandler(file_handler)

	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.INFO)
	console_handler.setFormatter(logging.Formatter(format_stream, datefmt='%H:%M:%S'))
	root_logger.addHandler(console_handler)
