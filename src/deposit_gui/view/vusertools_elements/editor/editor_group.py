from deposit_gui.view.vusertools_elements.user_elements import user_groups
from deposit_gui.view.vusertools_elements.editor.editor_frame import (EditorFrame)

from PySide6 import (QtWidgets, QtCore)

class EditorGroup(QtWidgets.QGroupBox):
	
	def __init__(self, element, form_editor, user_group = None):
		
		self.label_edit = None
		self.element = element
		self.group = None
		self.hovered = False
		self.selected = False
		self.bold = False
		self.form_editor = form_editor
		
		QtWidgets.QGroupBox.__init__(self, self.element)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		if user_group is None:
			user_group = getattr(user_groups, element)("", "Label")
		self.group = user_group
		
		self.label_edit = QtWidgets.QLineEdit()
		if not self.group.label:
			self.label_edit.setPlaceholderText("Label")
		else:
			self.label_edit.setText(self.group.label)
		form = QtWidgets.QFrame()
		form_layout = QtWidgets.QFormLayout()
		form.setLayout(form_layout)
		form.layout().setContentsMargins(0, 0, 0, 0)
		form.layout().addRow("Label:", self.label_edit)
		self.layout().addWidget(form)
		
		self.controls_frame = QtWidgets.QFrame()
		controls_frame_layout = QtWidgets.QVBoxLayout()
		self.controls_frame.setLayout(controls_frame_layout)
		self.controls_frame.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.controls_frame)
		
		for member in self.group.members:
			self.add_frame(member.__class__.__name__, member)
		
		self.bold = "font-weight: bold;" in self.group.stylesheet
		
		self.update_stylesheet()
		
		self.setMouseTracking(True)
	
	def add_frame(self, element, user_control = None, before = None):
		
		if before is None:
			self.controls_frame.layout().addWidget(EditorFrame(element, self, user_control))
		else:
			idx = self.controls_frame.layout().indexOf(before)
			self.controls_frame.layout().insertWidget(idx, EditorFrame(element, self, user_control))
	
	def remove_control(self, element):
		
		self.controls_frame.layout().removeWidget(element)
	
	def user_element(self):
		
		label = self.label_edit.text()
		if not label:
			return None
		self.group.label = label
		self.group.stylesheet = "QGroupBox {font-weight: bold;}" if self.bold else ""
		self.group.members = []
		for element in self.controls_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorFrame):
				self.group.members.append(element.user_element())
		return self.group
		
	def get_selected(self):
		
		for element in self.controls_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorFrame):
				if element.selected:
					return element
		return None
		
	def deselect_all(self):
		
		for element in self.controls_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorFrame):
				element.setSelected(False)
	
	def update_stylesheet(self):
		
		stylesheet = ""
		if self.hovered:
			stylesheet += "%s {background: lightgrey;}" % (self.__class__.__name__)
		if self.selected:
			stylesheet += " %s {border: 2px solid grey;}" % (self.__class__.__name__)
		if self.bold:
			stylesheet += " %s {font-weight: bold;}" % (self.__class__.__name__)
		if stylesheet:
			self.setStyleSheet(stylesheet)
	
	def setSelected(self, state):
		
		self.selected = state
		self.update_stylesheet()
		self.form_editor.on_selection_changed()
	
	def setBold(self, state):
		
		self.bold = state
		self.update_stylesheet()
	
	def setParent(self, parent):
		
		if parent is None:
			for element in self.findChildren(QtWidgets.QWidget):
				element.setParent(None)
		QtWidgets.QGroupBox.setParent(self, parent)
	
	def enterEvent(self, event):
		
		self.hovered = True
		self.update_stylesheet()
	
	def leaveEvent(self, event):
		
		self.hovered = False
		self.update_stylesheet()
		
	def mousePressEvent(self, event):
		
		state = not self.selected
		self.form_editor.deselect_all()
		self.setSelected(state)
		self.form_editor.on_selection_changed()

