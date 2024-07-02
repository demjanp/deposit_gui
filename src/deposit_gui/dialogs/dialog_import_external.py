from deposit_gui.dgui.abstract_subview import AbstractSubview

from PySide6 import (QtWidgets, QtCore, QtGui)

class DialogImportExternal(AbstractSubview, QtWidgets.QFrame):
	
	def __init__(self, dialog, n_rows, classes, relations):
		
		QtWidgets.QFrame.__init__(self)
		AbstractSubview.__init__(self)
		
		self._classes = classes
		self._checkboxes = []
		self._relcontrols = {}
		
		dialog.set_title("Import External Data")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		self.setMinimumWidth(256)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		frame = QtWidgets.QFrame()
		frame_layout = QtWidgets.QHBoxLayout()
		frame.setLayout(frame_layout)
		frame.layout().setContentsMargins(0, 0, 0, 0)
		
		grid = QtWidgets.QFrame()
		self.layout().addWidget(frame)
		frame.layout().addWidget(grid)
		frame.layout().addStretch()
		
		grid_layout = QtWidgets.QGridLayout()
		grid.setLayout(grid_layout)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Rows:</b>"), 0, 0)
		grid.layout().addWidget(QtWidgets.QLabel("%d" % (n_rows)), 0, 1)
		grid.layout().addWidget(QtWidgets.QLabel(), 1, 0)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Class</b>"), 2, 0)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Unique</b>"), 2, 1)
		idx = 0
		for idx, name in enumerate(self._classes):
			self._checkboxes.append(QtWidgets.QCheckBox())
			self._checkboxes[-1]._name = name
			grid.layout().addWidget(QtWidgets.QLabel(name), idx + 3, 0)
			grid.layout().addWidget(self._checkboxes[-1], idx + 3, 1)
		self._match_empty = QtWidgets.QCheckBox("Match Empty Descriptors")
		self._match_empty.setToolTip("If checked, match also empty Descriptors, otherwise add them.")
		grid.layout().addWidget(self._match_empty, idx + 4, 0)
		grid.layout().addWidget(QtWidgets.QLabel(), idx + 5, 0)
		grid.layout().addWidget(QtWidgets.QLabel("<b>Relations:</b>"), idx + 6, 0)
		
		self.form = QtWidgets.QFrame()
		form_layout = QtWidgets.QGridLayout()
		self.form.setLayout(form_layout)
		margins = self.form.layout().contentsMargins()
		margins.setTop(0)
		self.form.layout().setContentsMargins(margins)
		self.layout().addWidget(self.form)
		
		row = 0
		for src, label, tgt in relations:
			ctrls = []
			ctrls.append(QtWidgets.QComboBox())
			ctrls[-1].addItems(self._classes)
			ctrls[-1].setCurrentIndex(self._classes.index(src))
			ctrls[-1].setEditable(True)
			ctrls.append(QtWidgets.QLineEdit(label))
			ctrls.append(QtWidgets.QComboBox())
			ctrls[-1].addItems(self._classes)
			ctrls[-1].setCurrentIndex(self._classes.index(tgt))
			ctrls[-1].setEditable(True)
			ctrls.append(RemoveButton(row, self.get_icon("trash.svg")))
			ctrls[-1].signal_clicked.connect(self.on_remove)
			
			self._relcontrols[row] = ctrls
			
			self.form.layout().addWidget(ctrls[0], row, 0)
			self.form.layout().addWidget(ctrls[1], row, 1)
			self.form.layout().addWidget(ctrls[2], row, 2)
			self.form.layout().addWidget(ctrls[3], row, 3)
			
			row += 1
		
		button_add = QtWidgets.QToolButton()
		button_add.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
		button_add.setIcon(self.get_icon("link.svg"))
		button_add.setIconSize(QtCore.QSize(24,24))
		button_add.setText("Add")
		button_add.clicked.connect(self.on_add)
		
		frame = QtWidgets.QFrame()
		frame_layout = QtWidgets.QHBoxLayout()
		frame.setLayout(frame_layout)
		frame.layout().addStretch()
		frame.layout().addWidget(button_add)
		frame.layout().addStretch()
		self.layout().addWidget(frame)
		
	def add_row(self):
		
		row = self.form.layout().rowCount()
		
		ctrls = []
		ctrls.append(QtWidgets.QComboBox())
		ctrls[-1].addItems([""] + self._classes)
		ctrls[-1].setEditable(True)
		ctrls.append(QtWidgets.QLineEdit(""))
		ctrls.append(QtWidgets.QComboBox())
		ctrls[-1].addItems([""] + self._classes)
		ctrls[-1].setEditable(True)
		ctrls.append(RemoveButton(row, self.get_icon("trash.svg")))
		ctrls[-1].signal_clicked.connect(self.on_remove)
		
		self._relcontrols[row] = ctrls
		
		self.form.layout().addWidget(ctrls[0], row, 0)
		self.form.layout().addWidget(ctrls[1], row, 1)
		self.form.layout().addWidget(ctrls[2], row, 2)
		self.form.layout().addWidget(ctrls[3], row, 3)
	
	@QtCore.Slot(int)
	def on_remove(self, row):
		
		for col in range(4):
			item = self.form.layout().itemAtPosition(row, col)
			item.widget().deleteLater()
		del self._relcontrols[row]
	
	@QtCore.Slot()
	def on_add(self):
		
		self.add_row()
	
	def get_unique(self):
		
		unique = set()
		for checkbox in self._checkboxes:
			if checkbox.isChecked():
				unique.add(checkbox._name)
		return unique
	
	def get_relations(self):
		
		relations = set()
		for row in self._relcontrols:
			combo_src, edit_label, combo_tgt, _ = self._relcontrols[row]
			src = combo_src.currentText().strip()
			tgt = combo_tgt.currentText().strip()
			label = edit_label.text().strip()
			if label and (src in self._classes) and (tgt in self._classes):
				relations.add((src, label, tgt))
		return relations
	
	def get_match_empty(self):
		
		if self._match_empty.isChecked():
			return True
		return False


class RemoveButton(QtWidgets.QToolButton):
	
	signal_clicked = QtCore.Signal(int)
	
	def __init__(self, row, icon):
		
		QtWidgets.QToolButton.__init__(self)
		
		self.setIcon(icon)
		self.setToolTip("Remove Relation")
		
		self._row = row
		self.clicked.connect(self.on_clicked)
	
	@QtCore.Slot()
	def on_clicked(self):
		
		self.signal_clicked.emit(self._row)
		