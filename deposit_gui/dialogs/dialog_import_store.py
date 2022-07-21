from PySide2 import (QtWidgets, QtCore, QtGui)

class DialogImportStore(QtWidgets.QFrame):
	
	def __init__(self, dialog, objects, classes):
		
		QtWidgets.QFrame.__init__(self)
		
		self._checkboxes = []
		
		dialog.set_title("Import Store")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		self.setMinimumWidth(256)
		
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		grid = QtWidgets.QFrame()
		grid.setLayout(QtWidgets.QGridLayout())
		self.layout().addWidget(grid)
		self.layout().addStretch()
		
		grid.layout().addWidget(QtWidgets.QLabel("<b>Objects:</b>"), 0, 0)
		grid.layout().addWidget(QtWidgets.QLabel("%d" % (len(objects))), 0, 1)
		grid.layout().addWidget(QtWidgets.QLabel(), 1, 0)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Class</b>"), 2, 0)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Unique</b>"), 2, 1)
		for idx, name in enumerate(classes):
			self._checkboxes.append(QtWidgets.QCheckBox())
			self._checkboxes[-1]._name = name
			grid.layout().addWidget(QtWidgets.QLabel(name), idx + 3, 0)
			grid.layout().addWidget(self._checkboxes[-1], idx + 3, 1)
	
	def get_unique(self):
		
		unique = set()
		for checkbox in self._checkboxes:
			if checkbox.isChecked():
				unique.add(checkbox._name)
		return unique


