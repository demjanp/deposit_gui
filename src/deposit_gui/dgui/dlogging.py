from PySide2 import (QtWidgets, QtCore)
import os
import sys
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
		self._append_timer = QtCore.QTimer()
		self._append_timer.setSingleShot(True)
		self._append_timer.timeout.connect(self.on_append_timer)
		
		path = os.path.join(str(Path.home()), app_name)
		if not os.path.isdir(path):
			os.mkdir(path)
		self.log_path = os.path.join(path, "%s.log" % (app_name))
		log_handler = RotatingFileHandler(self.log_path, mode = "a", maxBytes = 5*1024*1024, backupCount = 2, encoding = None, delay = 0)
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
		self._append_data.append(text)
		if QtCore.QThread.currentThread() != self.thread():
			self.on_append_timer()
			return
		self._append_timer.start(100)
		QtWidgets.QApplication.processEvents()
	
	def flush(self):
		
		if not self._append_data:
			return
		text = "\n".join(self._append_data)
		self.logged.emit(text)
		for row in self._append_data:
			self.logger.info(row, extra = {"version": self.version})
		self._append_data = []
	
	@QtCore.Slot()
	def on_append_timer(self):
		
		self.flush()
