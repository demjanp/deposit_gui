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
		self._n_writes = 0
		
		self.key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\%s" % (self.app_name))
		for i in range(winreg.QueryInfoKey(self.key)[1]):
			var, value, _ = winreg.EnumValue(self.key, i)
			self._vars[var] = value
		
		self._set_data = {}
	
	def get(self, var):
		
		if var not in self._vars:
			return ""
#		print("registry get", var, self._vars[var])  # DEBUG crashes if active
		return self._vars[var]
	
	def set(self, var, value):
		
		self._vars[var] = value
		self._set_data[var] = value
		self._n_writes += 1
		
		if self._n_writes > 10:
			self.flush()
	
	def vars(self):
		
		return list(self._vars.keys())
	
	def flush(self):
		
		for var in self._set_data:
			winreg.SetValueEx(self.key, var, 0, winreg.REG_SZ, self._set_data[var])
		self._set_data = {}
		self._n_writes = 0
