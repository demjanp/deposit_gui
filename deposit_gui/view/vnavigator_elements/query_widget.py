from deposit_gui.view.vnavigator_elements.query_list import QueryList

from PySide2 import (QtWidgets, QtCore, QtGui)

class QueryWidget(QtWidgets.QWidget):
	
	def __init__(self, vnavigator):
		
		QtWidgets.QWidget.__init__(self, vnavigator)
		
		self._vnavigator = vnavigator
		self._querylist = QueryList(self._vnavigator)
		self._footer = QueryFooter(self._vnavigator)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.layout().addWidget(self._querylist)
		
		self.layout().addWidget(self._footer)
		
		self.update_footer()
	
	def populate(self, queries):
		
		self._querylist.populate(queries)
	
	def get_selected(self):
		
		return self._querylist.get_selected()
	
	def update_footer(self):
		
		selected = self.get_selected()
		
		self._footer.button_edit.setEnabled(len(selected) == 1)
		self._footer.button_remove.setEnabled(len(selected) > 0)

class QueryFooter(QtWidgets.QFrame):
	
	def __init__(self, vnavigator):

		QtWidgets.QFrame.__init__(self)

		self._vnavigator = vnavigator
		
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(6)
		
		self.layout().addStretch()
		
		self.button_add = QtWidgets.QToolButton(self)
		self.button_add.setIcon(self._vnavigator.get_icon("add_query.svg"))
		self.button_add.setIconSize(QtCore.QSize(32, 32))
		self.button_add.setToolTip("Add Query")
		self.button_add.clicked.connect(self._vnavigator.on_query_add)
		self.layout().addWidget(self.button_add)
		
		self.button_edit = QtWidgets.QToolButton(self)
		self.button_edit.setIcon(self._vnavigator.get_icon("edit_query.svg"))
		self.button_edit.setIconSize(QtCore.QSize(32, 32))
		self.button_edit.setToolTip("Edit Query")
		self.button_edit.clicked.connect(self._vnavigator.on_query_edit)
		self.layout().addWidget(self.button_edit)
		
		self.button_remove = QtWidgets.QToolButton(self)
		self.button_remove.setIcon(self._vnavigator.get_icon("remove_query.svg"))
		self.button_remove.setIconSize(QtCore.QSize(32, 32))
		self.button_remove.setToolTip("Remove Query")
		self.button_remove.clicked.connect(self._vnavigator.on_query_remove)
		self.layout().addWidget(self.button_remove)

