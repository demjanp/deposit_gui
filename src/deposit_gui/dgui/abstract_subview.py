from PySide6 import (QtWidgets, QtCore, QtGui)

from deposit_gui import res as icon_resources
import deposit_gui

import os

class AbstractSubview(object):
	
	def __init__(self, vmain = None) -> None:
		
		self.vmain = vmain
		self._res_folder = None
	
	def set_res_folder(self, path):
		
		self._res_folder = path
	
	def get_icon(self, name: str) -> QtGui.QIcon:
		
		if self._res_folder is not None:
			path = os.path.join(self._res_folder, name)
			if os.path.isfile(path):
				return QtGui.QIcon(path)
		path = os.path.join(os.path.dirname(icon_resources.__file__), name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		path = os.path.join(os.path.dirname(deposit_gui.__file__), "res", name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		raise Exception("Could not load icon %s" % (name))
