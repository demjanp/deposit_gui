from deposit_gui.dgui.abstract_subview import AbstractSubview

from PySide6 import (QtWidgets, QtCore, QtGui)

class AbstractOutsideFrame(AbstractSubview, QtWidgets.QMainWindow):
	
	def __init__(self):
		
		AbstractSubview.__init__(self)
		QtWidgets.QMainWindow.__init__(self)
		
	
	def title(self):
		# re-implement
		
		return "MDIAreaFrame"
	
	def icon(self):
		# re-implement
		
		return "dep_cube.svg"

