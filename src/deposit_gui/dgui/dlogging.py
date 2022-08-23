from PySide2 import (QtWidgets, QtCore)
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

class DLogging(QtCore.QObject):
	
	logged = QtCore.Signal(str)
	
	def __init__(self, app_name, version):
		
		QtCore.QObject.__init__(self)
		
		self.log_path = ""
		self.version = version
		
		self._append_data = []
		
		path = os.path.join(str(Path.home()), app_name)
		if not os.path.isdir(path):
			os.mkdir(path)
		self.log_path = os.path.join(path, "%s.log" % (app_name))
		log_handler = RotatingFileHandler(self.log_path, mode = "a", maxBytes = 100*1024, backupCount = 2, encoding = None, delay = 0)
		log_handler.setFormatter(logging.Formatter(fmt = "%(asctime)s v%(version)s %(message)s", datefmt = "%Y-%m-%d %H:%M:%S"))
		log_handler.setLevel(logging.INFO)
		self.logger = logging.getLogger("root")
		self.logger.setLevel(logging.INFO)
		self.logger.addHandler(log_handler)
	
	def get_log_path(self):
		
		return self.log_path
	
	def append(self, text):
		
		text = str(text).strip().strip("\n").strip("\r")
		if not text:
			return
		self.logger.info(text, extra = {"version": self.version})
		self.logged.emit(text)
