from deposit_gui.view.vusertools_elements.user_elements.user_controls import (Select)

from deposit.utils.fnc_serialize import (select_to_class_descr)

from PySide2 import (QtWidgets)

class EditorSelect(QtWidgets.QFrame):
	
	def __init__(self, form_editor, user_select = None):
		
		self.label_edit = None
		self.user_select = None
		self.selected = False
		self.form_editor = form_editor
		
		QtWidgets.QFrame.__init__(self)
		
		if user_select is None:
			user_select = Select("", "", "", "")
		self.user_select = user_select
		
		self.setStyleSheet("%s:hover {background: grey;}" % (self.__class__.__name__))
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		dclass, descriptor = self.user_select.dclass, self.user_select.descriptor
		self.select = QtWidgets.QLineEdit()
		if (not dclass) or (not descriptor):
			self.select.setPlaceholderText("[Class].[Descriptor]")
		else:
			self.select.setText("[%s].[%s]" % (dclass, descriptor))
		self.layout().addWidget(self.select)
	
	def select_text(self):
		
		return self.select.text().strip()
	
	def user_element(self):
		
		select = select_to_class_descr(self.select_text())
		if not select:
			return None
		
		self.user_select.dclass = select[0]
		self.user_select.descriptor = select[1]
		return self.user_select
	
	def setSelected(self, state):
		
		if state:
			self.form_editor.deselect_all()
			self.setStyleSheet("%s {border: 2px solid grey;} %s:hover {background: grey;}" % (self.__class__.__name__, self.__class__.__name__))
		else:
			self.setStyleSheet("%s:hover {background: grey;}" % (self.__class__.__name__))
		self.selected = state
		self.form_editor.on_selection_changed()
	
	def mousePressEvent(self, event):
		
		self.setSelected(not self.selected)

