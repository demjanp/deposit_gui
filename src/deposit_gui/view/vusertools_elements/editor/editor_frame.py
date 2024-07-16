from deposit_gui.view.vusertools_elements.editor import editor_controls as EditorControls

from deposit.utils.fnc_serialize import (select_to_class_descr)

from PySide6 import (QtWidgets)

class EditorFrame(QtWidgets.QFrame):
	
	def __init__(self, element, form_editor, user_control = None):
		
		self.label_edit = None
		self.ctrl = None
		self.selected = False
		self.bold = False
		self.form_editor = form_editor
		
		QtWidgets.QFrame.__init__(self)

		layout = QtWidgets.QFormLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		self.ctrl = getattr(EditorControls, element)(user_control)
		label = self.ctrl.user_control.label
		self.label_edit = QtWidgets.QLineEdit()
		if not label:
			self.label_edit.setPlaceholderText("Label")
		else:
			self.label_edit.setText(label)
		self.layout().addRow(self.label_edit, self.ctrl)
		
		self.bold = "font-weight: bold;" in self.ctrl.user_control.stylesheet
		
		self.update_stylesheet()
	
	def user_element(self):
		
		label = self.label_edit.text()
		select = select_to_class_descr(self.ctrl.select_text())
		
		if (not label) or (not select):
			return None
		
		self.ctrl.user_control.label = label
		self.ctrl.user_control.stylesheet = "QLabel {font-weight: bold;}" if self.bold else ""
		self.ctrl.user_control.dclass = select[0]
		self.ctrl.user_control.descriptor = select[1]
		return self.ctrl.user_control
	
	def update_stylesheet(self):
		
		stylesheet = "%s:hover {background: grey;}" % (self.__class__.__name__)
		if self.selected:
			stylesheet += " %s {border: 2px solid grey;} " % (self.__class__.__name__)
		self.setStyleSheet(stylesheet)
		if self.bold:
			self.label_edit.setStyleSheet("QLineEdit {font-weight: bold;}")
		else:
			self.label_edit.setStyleSheet("{}")
	
	def setSelected(self, state):
		
		self.selected = state
		self.update_stylesheet()
	
	def setBold(self, state):
		
		self.bold = state
		self.update_stylesheet()
	
	def mousePressEvent(self, event):
		
		state = not self.selected
		form_editor = self.form_editor
		if hasattr(form_editor, "form_editor"):
			form_editor = form_editor.form_editor
		form_editor.deselect_all()
		self.setSelected(state)
		form_editor.on_selection_changed()

