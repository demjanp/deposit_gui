from PySide6 import (QtWidgets, QtCore, QtGui)

class DProgress(object):

	def __init__(self, parent=None):
		self._maximum = None
	
	def cancel_pressed(self):    
		return False
	
	def show(self, text=""):
		QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
	
	def stop(self):
		QtWidgets.QApplication.restoreOverrideCursor()
		self._maximum = None
	
	def update_state(self, text=None, value=None, maximum=None):
		
		if maximum is not None:
			self._maximum = maximum
		if (value is not None) and (self._maximum is not None):
			if value >= self._maximum:
				self.stop()
