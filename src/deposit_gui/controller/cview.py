from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.view.view import View

from PySide2 import (QtWidgets, QtCore, QtGui)
from pathlib import Path
import os

class CView(AbstractSubcontroller):
	
	def __init__(self, cmain, cnavigator, cmdiarea) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._view = View(cnavigator._vnavigator, cmdiarea._vmdiarea)
		
		self.progress = self._view.progress
		
		self._view.signal_close.connect(self.on_close)
		
		self._controls = {}
		for name in dir(self):
			if name.startswith("on_ctrl_"):
				ctrlname = name[3:]
				for frame in [self._view.controls_frame, self._view.popup_controls_frame]:
					if hasattr(frame, ctrlname):
						self._controls[ctrlname] = getattr(frame, ctrlname)
						self._controls[ctrlname].signal_changed.connect(getattr(self, name))

	def show(self):
		
		self._view.show()
	
	def update(self):
		
		for name in self._controls:
			if hasattr(self, "update_%s" % (name)):
				data = getattr(self, "update_%s" % (name))()
				value = data.get("value", None)
				enabled = data.get("enabled", None)
				if value is not None:
					self._controls[name].set_value(value)
				if enabled is not None:
					self._controls[name].setEnabled(enabled)
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	@QtCore.Slot()
	def on_close(self):
		
		self.cmain.on_close()
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	def set_title(self, title):
		
		self._view.set_title(title)
	
	def get_default_folder(self):
		
		folder = self._view.get_recent_dir()
		if folder:
			return folder
		
		if self.cmain.cmodel.has_local_folder():
			return self.cmain.cmodel.get_folder()
		
		return str(Path.home())
	
	def get_save_path(self, caption, filter):
		# returns path, format
		
		path, format = QtWidgets.QFileDialog.getSaveFileName(self._view, dir = self.get_default_folder(), caption = caption, filter = filter)
		
		return path, format
	
	def get_load_path(self, caption, filter):
		
		path, format = QtWidgets.QFileDialog.getOpenFileName(self._view, dir = self.get_default_folder(), caption = caption, filter = filter)
		
		return path, format
	
	def get_logging_path(self):
		
		return self._view.logging.get_log_path()
	
	def get_existing_folder(self, caption):
		
		folder = QtWidgets.QFileDialog.getExistingDirectory(self._view, dir = self.get_default_folder(), caption = caption)
		
		return folder
	
	def get_recent_dir(self):
		
		return self._view.get_recent_dir()
	
	def set_recent_dir(self, path):
		
		if os.path.isfile(path):
			path = os.path.dirname(path)
		if not os.path.isdir(path):
			return
		self._view.set_recent_dir(path)
	
	def set_status_message(self, text):
		
		self._view.statusbar.message(text)
	
	def show_information(self, caption, text):
		
		QtWidgets.QMessageBox.information(self._view, caption, text)
	
	def show_warning(self, caption, text):
		
		QtWidgets.QMessageBox.warning(self._view, caption, text)

	
	def show_question(self, caption, text):
		
		reply = QtWidgets.QMessageBox.question(self._view, caption, text)
		
		return reply == QtWidgets.QMessageBox.Yes

