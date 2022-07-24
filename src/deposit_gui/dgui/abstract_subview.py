from PySide2 import (QtWidgets, QtCore, QtGui)

from deposit_gui import res as icon_resources
import deposit_gui

import os

class AbstractSubview(QtCore.QObject):
	
	def __init__(self, vmain = None) -> None:
		
		QtCore.QObject.__init__(self)
		
		self.vmain = vmain
	
	def get_icon(self, name: str) -> QtGui.QIcon:
		
		path = os.path.join(os.path.dirname(icon_resources.__file__), name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		path = os.path.join(os.path.dirname(deposit_gui.__file__), "res", name)
		if os.path.isfile(path):
			return QtGui.QIcon(path)
		raise Exception("Could not load icon %s" % (name))
