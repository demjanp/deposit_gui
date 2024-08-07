
from PySide6 import (QtWidgets, QtCore, QtGui)

class DialogColumn(QtWidgets.QFrame):
	
	def __init__(self):
		
		QtWidgets.QFrame.__init__(self)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addStretch()
		
#		self.setStyleSheet("DialogColumn {border: 1px solid gray;}")
	
	def add_widget(self, widget):
		
		self.layout().insertWidget(self.layout().count() - 1, widget)
