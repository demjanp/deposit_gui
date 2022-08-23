'''
DMainWindow(QtWidgets.QMainWindow)
	.registry
		.get(var)
		.set(var, value)
		.vars()
		.flush()
'''
from deposit_gui.dgui.dregistry import DRegistry

from PySide2 import (QtWidgets, QtCore, QtGui)

class DMainWindow(QtWidgets.QMainWindow):
	
	APP_NAME = "DView"
	REG_PREFIX = ""
	
	def __init__(self):
		
		self._current_geometry = None
		self._previous_geometry = None
		
		QtWidgets.QMainWindow.__init__(self)
		
		self.registry = DRegistry(self.APP_NAME)
		
		self._load_geometry()
		self._current_geometry = self._get_geometry()
		self._previous_geometry = self._current_geometry
		self._load_window_state()
	
	def _load_geometry(self):
		
		geometry = self.registry.get(self.REG_PREFIX + "window_geometry")
		if geometry:
			geometry = geometry[1:].strip("'")
			self.restoreGeometry(QtCore.QByteArray().fromPercentEncoding(
				bytearray(geometry, "utf-8"))
			)
		
	def _get_geometry(self):
		
		return str(self.saveGeometry().toPercentEncoding())
		
	def _save_geometry(self, geometry = None):
		
		geometry = self._get_geometry()
		if self.isVisible():
			if geometry:
				self.registry.set(self.REG_PREFIX + "window_geometry", geometry)
		return geometry
		
	def _load_window_state(self):
		
		state = self.registry.get(self.REG_PREFIX + "widow_maximized")
		if state:
			if int(state) == 1:
				self.showMaximized()
			else:
				self.showNormal()
		
	def _save_window_state(self):
		
		if self.isVisible():
			self.registry.set(
				self.REG_PREFIX + "widow_maximized",
				str(int(self.isMaximized()))
			)
	
	# overriden QMainWindow methods
	
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
		QtWidgets.QMainWindow.closeEvent(self, event)

