from PySide6 import (QtWidgets, QtCore, QtGui)

class DConnectTabMemory(QtWidgets.QFrame):
	
	def __init__(self, parent):
		
		QtWidgets.QFrame.__init__(self, parent)
		
		self.parent = parent
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		label = QtWidgets.QLabel("Create a new database in memory.\n\n")
		label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		
		self.connect_button = QtWidgets.QPushButton("Create")
		self.connect_button.clicked.connect(self.on_connect)
		
		self.layout().addStretch()
		self.layout().addWidget(label)
		self.layout().addWidget(self.connect_button, alignment = QtCore.Qt.AlignmentFlag.AlignCenter)
		self.layout().addStretch()
	
	@QtCore.Slot()
	def on_connect(self):
		
		self.parent.on_connect(datasource = "Memory")

