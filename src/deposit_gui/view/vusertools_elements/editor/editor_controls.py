from deposit_gui.view.vusertools_elements.user_elements import user_controls as UserControls

from PySide6 import (QtWidgets)

class EditorControl(object):
	
	def __init__(self, user_control = None):
		
		if user_control is None:
			user_control = getattr(UserControls, self.__class__.__name__)("", "", "", "")
		self.user_control = user_control
	
	def select_text(self):
		
		return ""

class LineEdit(EditorControl, QtWidgets.QLineEdit):
	
	def __init__(self, user_control = None):
		
		EditorControl.__init__(self, user_control)
		QtWidgets.QLineEdit.__init__(self)
		dclass, descriptor = self.user_control.dclass, self.user_control.descriptor
		if (not dclass) or (not descriptor):
			self.setPlaceholderText("[Class].[Descriptor]")
		else:
			self.setText("[%s].[%s]" % (dclass, descriptor))
		
	def select_text(self):
		
		return self.text().strip()

class PlainTextEdit(EditorControl, QtWidgets.QPlainTextEdit):
	
	def __init__(self, user_control = None):
		
		EditorControl.__init__(self, user_control)
		QtWidgets.QPlainTextEdit.__init__(self)
		self.setFixedHeight(100)
		dclass, descriptor = self.user_control.dclass, self.user_control.descriptor
		if (not dclass) or (not descriptor):
			self.setPlaceholderText("[Class].[Descriptor]")
		else:
			self.setPlainText("[%s].[%s]" % (dclass, descriptor))
		
	def select_text(self):
		
		return self.toPlainText().strip()

class ComboBox(EditorControl, QtWidgets.QComboBox):
	
	def __init__(self, user_control = None):
		
		EditorControl.__init__(self, user_control)
		QtWidgets.QComboBox.__init__(self)
		self.setEditable(True)
		dclass, descriptor = self.user_control.dclass, self.user_control.descriptor
		if (not dclass) or (not descriptor):
			self.lineEdit().setPlaceholderText("[Class].[Descriptor]")
		else:
			self.setCurrentText("[%s].[%s]" % (dclass, descriptor))
	
	def select_text(self):
		
		return self.currentText().strip()

class CheckBox(EditorControl, QtWidgets.QFrame):
	
	def __init__(self, user_control = None):
		
		EditorControl.__init__(self, user_control)
		QtWidgets.QFrame.__init__(self)
		
		layout = QtWidgets.QHBoxLayout()
		self.setLayout(layout)
		
		dclass, descriptor = self.user_control.dclass, self.user_control.descriptor
		self.select = QtWidgets.QLineEdit()
		if (not dclass) or (not descriptor):
			self.select.setPlaceholderText("[Class].[Descriptor]")
		else:
			self.select.setText("[%s].[%s]" % (dclass, descriptor))
		
		self.checkbox = QtWidgets.QCheckBox()
		self.checkbox.setChecked(True)
		self.checkbox.setEnabled(False)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.checkbox)
		self.layout().addWidget(self.select)
		self.layout().addStretch()
	
	def select_text(self):
		
		return self.select.text().strip()

class Select(EditorControl, QtWidgets.QLineEdit):
	
	def __init__(self, user_control = None):
		
		EditorControl.__init__(self, user_control)
		QtWidgets.QLineEdit.__init__(self)
		dclass, descriptor = self.user_control.dclass, self.user_control.descriptor
		if (not dclass) or (not descriptor):
			self.setPlaceholderText("[Class].[Descriptor]")
		else:
			self.setText("[%s].[%s]" % (dclass, descriptor))
	
	def select_text(self):
		
		return self.text().strip()

