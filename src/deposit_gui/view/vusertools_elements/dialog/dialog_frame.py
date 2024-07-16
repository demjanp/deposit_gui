from deposit_gui.view.vusertools_elements.dialog import dialog_controls as DialogControls

from PySide6 import (QtWidgets)

class DialogFrame(QtWidgets.QFrame):
	
	def __init__(self, cmodel, user_control):
		# user_control = UserElement
		
		self._cmodel = cmodel
		self.user_control = user_control
		self.ctrl = None
		
		QtWidgets.QFrame.__init__(self)
		
		self.ctrl = getattr(DialogControls, user_control.__class__.__name__)(self._cmodel, self.user_control)
		
		layout = QtWidgets.QFormLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapLongRows)
		label = QtWidgets.QLabel("%s:" % (self.user_control.label))
		if self.user_control.stylesheet:
			label.setStyleSheet(self.user_control.stylesheet)
		self.layout().addRow(label, self.ctrl)
	
	@property
	def dclass(self):
		
		return self.user_control.dclass
	
	@property
	def descriptor(self):
		
		return self.user_control.descriptor
	
	def set_value(self, value, obj_id = None):
		
		self.ctrl.set_value(value)
		self.ctrl.set_object(obj_id)
	
	def populate_lookup(self):
		
		self.ctrl.populate_lookup()
	
	def get_value(self):
		
		return self.ctrl.get_value()
	
	def get_object(self):
		
		return self.ctrl.obj_id

