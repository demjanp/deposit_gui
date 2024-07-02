from PySide6 import (QtCore)

class AbstractSubcontroller(QtCore.QObject):
	
	def __init__(self, cmain) -> None:
		
		QtCore.QObject.__init__(self)
		
		self.cmain = cmain
