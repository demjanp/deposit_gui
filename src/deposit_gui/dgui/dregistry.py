
'''
Generic class to be re-used also by Deposit in the future
'''


from PySide2 import QtWidgets, QtCore
import sys

class DRegistry(QtCore.QObject):
    def __init__(self, app_name):
        QtCore.QObject.__init__(self)
        
        self.app_name = app_name
        self._vars = {}
        self._set_data = {}
        self._n_writes = 0
        
        if sys.platform == "win32":
            import winreg
            self.key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\%s" % self.app_name)
            for i in range(winreg.QueryInfoKey(self.key)[1]):
                var, value, _ = winreg.EnumValue(self.key, i)
                self._vars[var] = value
        elif sys.platform == "darwin":
            self.preferences = QtCore.QSettings("LAP 4")
            self.preferences.beginGroup(self.app_name)
            keys = self.preferences.allKeys()
            for key in keys:
                self._vars[key] = self.preferences.value(key)
            self.preferences.endGroup()
        elif sys.platform.startswith("linux"):
            raise NotImplmentedError("Linux not supported")
        else:
            raise Exception("Unknown OS")
	
    def get(self, var):
        if var not in self._vars:
            return ""
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
        if sys.platform == "win32":
            import winreg
            for var in self._set_data:
                winreg.SetValueEx(self.key, var, 0, winreg.REG_SZ, self._set_data[var])
        elif sys.platform == "darwin":
            self.preferences.beginGroup(self.app_name)
            for var in self._set_data:
                self.preferences.setValue(var, self._set_data[var])
            self.preferences.endGroup()
        
        self._set_data = {}
        self._n_writes = 0
