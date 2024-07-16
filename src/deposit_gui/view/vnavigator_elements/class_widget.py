from deposit_gui.view.vnavigator_elements.class_list import ClassList

from PySide6 import (QtWidgets, QtCore, QtGui)

class ClassWidget(QtWidgets.QWidget):
	
	def __init__(self, vnavigator):
		
		QtWidgets.QWidget.__init__(self, vnavigator)
		
		self._vnavigator = vnavigator
		self._classlist = ClassList(self._vnavigator)
		self._footer = ClassFooter(self._vnavigator)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.layout().addWidget(self._classlist)
		
		self.layout().addWidget(self._footer)
		
		self.update_footer()
	
	def populate(self, classes):
		
		self._classlist.populate(classes)
	
	def get_selected(self):
		
		return self._classlist.get_selected()
	
	def get_selected_is_descriptor(self):
		
		return self._classlist.get_selected_is_descriptor()
	
	def get_selected_parent(self):
		
		return self._classlist.get_selected_parent()
	
	def get_items_around_selected(self):
		
		return self._classlist.get_items_around_selected()
	
	def select_one_above(self):
		
		self._classlist.select_one_above()
	
	def select_one_below(self):
		
		self._classlist.select_one_below()
	
	def deselect_all(self):
		
		self._classlist.clearSelection()
	
	def update_footer(self):
		
		selected = self.get_selected()
		enabled1 = (len(selected) == 1) and (selected[0] != "!*")
		is_descriptor = self.get_selected_is_descriptor()
		enabled2 = enabled1 and not is_descriptor
		
		self._footer.button_add_desciptor.setEnabled(enabled2)
		self._footer.button_del_desciptor.setEnabled(is_descriptor)
		self._footer.button_rename.setEnabled(enabled1)
		self._footer.button_up.setEnabled(enabled1)
		self._footer.button_down.setEnabled(enabled1)
		self._footer.button_remove.setEnabled((len([name for name in selected if name != "!*"]) > 0))
	
class ClassFooter(QtWidgets.QFrame):
	
	def __init__(self, vnavigator):

		QtWidgets.QFrame.__init__(self)
		
		self._vnavigator = vnavigator

		layout = QtWidgets.QHBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(6)
		
		self.button_up = QtWidgets.QToolButton(self)
		self.button_up.setIcon(self._vnavigator.get_icon("up_small.svg"))
		self.button_up.setIconSize(QtCore.QSize(32, 32))
		self.button_up.setToolTip("Order Class Up")
		self.button_up.clicked.connect(self._vnavigator.on_class_up)
		self.layout().addWidget(self.button_up)
		
		self.button_down = QtWidgets.QToolButton(self)
		self.button_down.setIcon(self._vnavigator.get_icon("down_small.svg"))
		self.button_down.setIconSize(QtCore.QSize(32, 32))
		self.button_down.setToolTip("Order Class Down")
		self.button_down.clicked.connect(self._vnavigator.on_class_down)
		self.layout().addWidget(self.button_down)
		
		self.layout().addStretch()
		
		self.button_add = QtWidgets.QToolButton(self)
		self.button_add.setIcon(self._vnavigator.get_icon("add_class.svg"))
		self.button_add.setIconSize(QtCore.QSize(32, 32))
		self.button_add.setToolTip("Add Class")
		self.button_add.clicked.connect(self._vnavigator.on_class_add)
		self.layout().addWidget(self.button_add)
		
		self.button_add_desciptor = QtWidgets.QToolButton(self)
		self.button_add_desciptor.setIcon(self._vnavigator.get_icon("add_descriptor.svg"))
		self.button_add_desciptor.setIconSize(QtCore.QSize(32, 32))
		self.button_add_desciptor.setToolTip("Add Descriptor")
		self.button_add_desciptor.clicked.connect(self._vnavigator.on_class_add_descriptor)
		self.layout().addWidget(self.button_add_desciptor)
		
		self.button_del_desciptor = QtWidgets.QToolButton(self)
		self.button_del_desciptor.setIcon(self._vnavigator.get_icon("remove_descriptor.svg"))
		self.button_del_desciptor.setIconSize(QtCore.QSize(32, 32))
		self.button_del_desciptor.setToolTip("Remove Descriptor")
		self.button_del_desciptor.clicked.connect(self._vnavigator.on_class_del_descriptor)
		self.layout().addWidget(self.button_del_desciptor)
		
		self.button_rename = QtWidgets.QToolButton(self)
		self.button_rename.setIcon(self._vnavigator.get_icon("edit_class.svg"))
		self.button_rename.setIconSize(QtCore.QSize(32, 32))
		self.button_rename.setToolTip("Rename Class")
		self.button_rename.clicked.connect(self._vnavigator.on_class_rename)
		self.layout().addWidget(self.button_rename)
		
		self.button_remove = QtWidgets.QToolButton(self)
		self.button_remove.setIcon(self._vnavigator.get_icon("remove_class.svg"))
		self.button_remove.setIconSize(QtCore.QSize(32, 32))
		self.button_remove.setToolTip("Remove Class")
		self.button_remove.clicked.connect(self._vnavigator.on_class_remove)
		self.layout().addWidget(self.button_remove)
