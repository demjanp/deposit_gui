'''
Generic class to be re-used also by Deposit in the future
'''
'''
DView(QtWidgets.QMainWindow).
	.registry
		.get(var)
		.set(var, value)
		.vars()
		.flush()
	.progress
		.cancel_pressed()
		.show(text = "")
		.update_state(text = None, value = None, maximum = None)
	.statusbar
		.message(text)
	.logging
		.logged = Signal(text: str)
		.get_log_path()
		.append(text)
		.flush()
	.set_title(name)
	.set_icon(name)
	.get_icon(name)
'''

from deposit_gui.dgui.dregistry import DRegistry
from deposit_gui.dgui.dprogress import DProgress
from deposit_gui.dgui.dstatus_bar import DStatusBar
from deposit_gui.dgui.dlogging import DLogging

from deposit_gui import res as icon_resources
import deposit_gui

from PySide2 import (QtWidgets, QtCore, QtGui)
import traceback
import sys
import os

class DView(QtWidgets.QMainWindow):
	
	APP_NAME = "DView"
	VERSION = "0.0.0"
	
	def __init__(self):
		
		self._current_geometry = None
		self._previous_geometry = None
		
		QtWidgets.QMainWindow.__init__(self)
		
		self.registry = DRegistry(self.APP_NAME)
		self.progress = DProgress(self)
		self.statusbar = DStatusBar(self)
		self.logging = DLogging(self.APP_NAME, self.VERSION)
		
		self.set_title()
		self.setStatusBar(self.statusbar)
		self._load_geometry()
		self._current_geometry = self._get_geometry()
		self._previous_geometry = self._current_geometry
		self._load_window_state()
		
		sys.excepthook = self.exception_event
			
	# public methods
	
	def set_title(self, name: str = None) -> None:
		
		title = self.APP_NAME
		if name is None:
			self.setWindowTitle(title)
		else:
			self.setWindowTitle("%s - %s" % (name, title))
		
	def set_icon(self, name):
		
		self.setWindowIcon(self.get_icon(name))
		
	def get_icon(self, name: str) -> QtGui.QIcon:
		
		path = os.path.join(os.path.dirname(icon_resources.__file__), name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		path = os.path.join(os.path.dirname(deposit_gui.__file__), "res", name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		raise Exception("Could not load icon %s" % (name))
	
	# private methods
	
	def _load_geometry(self):
		
		geometry = self.registry.get("window_geometry")
		if geometry:
			geometry = geometry[1:].strip("'")
			self.restoreGeometry(QtCore.QByteArray().fromPercentEncoding(bytearray(geometry, "utf-8")))
		
	def _get_geometry(self):
		
		return str(self.saveGeometry().toPercentEncoding())
		
	def _save_geometry(self, geometry = None):
		
		geometry = self._get_geometry()
		if self.isVisible():
			if geometry:
				self.registry.set("window_geometry", geometry)
		return geometry
		
	def _load_window_state(self):
		
		state = self.registry.get("widow_maximized")
		if state:
			if int(state) == 1:
				self.showMaximized()
			else:
				self.showNormal()
		
	def _save_window_state(self):
		
		if self.isVisible():
			self.registry.set("widow_maximized", str(int(self.isMaximized())))
		
	# events
	
	def exception_event(self, typ, value, tb):
		
		text = "Exception: %s: %s\nTraceback: %s" % (str(typ), str(value), "".join(traceback.format_tb(tb)))
		self.logging.append(text)
		self.logging.flush()
		print(text)
	
	# overriden QMainWindow methods
	
	def keyPressEvent(self, event):
		
		for action in self.findChildren(QtWidgets.QAction):
			if action.isEnabled() and (
				action.shortcut() == QtGui.QKeySequence(event.key()+int(event.modifiers()))
			):
				action.trigger()
		
		QtWidgets.QMainWindow.keyPressEvent(self, event)
	
	def changeEvent(self, event):
		
		QtWidgets.QMainWindow.changeEvent(self, event)
		if event.type() ==  QtCore.QEvent.WindowStateChange:
			self._save_window_state()
			if self.isMaximized():
				self._save_geometry(self._previous_geometry)
	
	def resizeEvent(self, event):
		
		self._previous_geometry = self._current_geometry
		self._current_geometry = self._save_geometry()
		QtWidgets.QMainWindow.resizeEvent(self, event)
	
	def moveEvent(self, event):
		
		self._save_geometry()
		QtWidgets.QMainWindow.moveEvent(self, event)
	
	def closeEvent(self, event):
		
		self.registry.flush()
		self.logging.flush()
		QtWidgets.QMainWindow.closeEvent(self, event)

