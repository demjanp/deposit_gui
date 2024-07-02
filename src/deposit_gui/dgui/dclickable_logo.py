from PySide6 import (QtWidgets, QtCore, QtGui)
import webbrowser

class DClickableLogo(QtWidgets.QLabel):
	
	def __init__(self, image_path, link, *args, **kwargs):
		
		self.link = link
		
		QtWidgets.QLabel.__init__(self, *args, **kwargs)
		
		self.setPixmap(QtGui.QPixmap(image_path))
		self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
	
	def mousePressEvent(self, event):
		
		webbrowser.open(self.link)
		QtWidgets.QLabel.mousePressEvent(self, event)

