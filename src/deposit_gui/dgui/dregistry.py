'''
Generic class to be re-used also by Deposit in the future
'''

from PySide2 import (QtWidgets, QtCore)
import winreg

class DRegistry(QtCore.QObject):
	
	def __init__(self, app_name):
		
		QtCore.QObject.__init__(self)
		
		self.app_name = app_name
		self._vars = {}
		self.key = None
		
		self.key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\%s" % (self.app_name))
		for i in range(winreg.QueryInfoKey(self.key)[1]):
			var, value, _ = winreg.EnumValue(self.key, i)
			self._vars[var] = value
		
		self._set_data = {}
		self._set_timer = QtCore.QTimer()
		self._set_timer.setSingleShot(True)
		self._set_timer.timeout.connect(self.on_set_timer)
	
	def get(self, var):
		
		if var not in self._vars:
			return ""
		return self._vars[var]
	
	def set(self, var, value):
		
		self._vars[var] = value
		self._set_data[var] = value
		
		self._set_timer.start(100)
		QtWidgets.QApplication.processEvents()
	
	def vars(self):
		
		return list(self._vars.keys())
	
	def flush(self):
		
		self._set_timer.stop()
		for var in self._set_data:
			winreg.SetValueEx(self.key, var, 0, winreg.REG_SZ, self._set_data[var])
		self._set_data = {}
	
	@QtCore.Slot()
	def on_set_timer(self):
		
		self.flush()
