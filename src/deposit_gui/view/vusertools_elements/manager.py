from deposit_gui.view.vusertools_elements.editor.editor_form import (EditorForm)
from deposit_gui.view.vusertools_elements.editor.editor_query import (EditorQuery)
from deposit_gui.view.vusertools_elements.user_elements.user_tool import (UserTool)
from deposit_gui.view.vusertools_elements.user_elements.search_form import (SearchForm)
from deposit_gui.view.vusertools_elements.user_elements.entry_form import (EntryForm)
from deposit_gui.view.vusertools_elements.user_elements.query import (Query)

from PySide6 import (QtWidgets, QtCore)

class Manager(QtWidgets.QDialog):
	
	signal_export = QtCore.Signal(object)	# user_tool
	signal_import = QtCore.Signal()
	signal_del_tool = QtCore.Signal(list)	# [label, ...]
	
	def __init__(self, vusertools):
		
		QtWidgets.QDialog.__init__(self)
		
		self._vusertools = vusertools
		
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.setStyleSheet("QPushButton {Text-align:left;}")
		self.setWindowTitle("User Tool Manager")
		self.setMinimumWidth(300)
		self.setModal(True)
		layout = QtWidgets.QHBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		self.tool_list = QtWidgets.QListWidget()
		self.tool_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.controls = QtWidgets.QFrame()
		controls_layout = QtWidgets.QVBoxLayout()
		self.controls.setLayout(controls_layout)
		self.controls.layout().setContentsMargins(0, 0, 0, 0)
		
		self.button_add_query = QtWidgets.QPushButton("Add Query")
		self.button_add_query.setIcon(self._vusertools.get_icon("add_query.svg"))
		self.button_add_query.setIconSize(QtCore.QSize(32, 32))
		self.button_add_query.clicked.connect(self.on_add_query)
		self.controls.layout().addWidget(self.button_add_query)
		
		self.button_add_search = QtWidgets.QPushButton("Add Search Form")
		self.button_add_search.setIcon(self._vusertools.get_icon("add_search.svg"))
		self.button_add_search.setIconSize(QtCore.QSize(32, 32))
		self.button_add_search.clicked.connect(self.on_add_search)
		self.controls.layout().addWidget(self.button_add_search)
		
		self.button_add_entry = QtWidgets.QPushButton("Add Entry Form")
		self.button_add_entry.setIcon(self._vusertools.get_icon("add_form.svg"))
		self.button_add_entry.setIconSize(QtCore.QSize(32, 32))
		self.button_add_entry.clicked.connect(self.on_add_entry)
		self.controls.layout().addWidget(self.button_add_entry)
		
		self.button_edit = QtWidgets.QPushButton("Edit")
		self.button_edit.setIcon(self._vusertools.get_icon("edit.svg"))
		self.button_edit.setIconSize(QtCore.QSize(32, 32))
		self.button_edit.clicked.connect(self.on_edit)
		self.controls.layout().addWidget(self.button_edit)
		
		self.button_delete = QtWidgets.QPushButton("Delete")
		self.button_delete.setIcon(self._vusertools.get_icon("delete.svg"))
		self.button_delete.setIconSize(QtCore.QSize(32, 32))
		self.button_delete.clicked.connect(self.on_delete)
		self.controls.layout().addWidget(self.button_delete)
		
		self.button_order_up = QtWidgets.QPushButton("Order Up")
		self.button_order_up.setIcon(self._vusertools.get_icon("up_small.svg"))
		self.button_order_up.setIconSize(QtCore.QSize(32, 32))
		self.button_order_up.clicked.connect(self.on_order_up)
		self.controls.layout().addWidget(self.button_order_up)
		
		self.button_order_down = QtWidgets.QPushButton("Order Down")
		self.button_order_down.setIcon(self._vusertools.get_icon("down_small.svg"))
		self.button_order_down.setIconSize(QtCore.QSize(32, 32))
		self.button_order_down.clicked.connect(self.on_order_down)
		self.controls.layout().addWidget(self.button_order_down)
		
		self.button_export = QtWidgets.QPushButton("Export")
		self.button_export.setIcon(self._vusertools.get_icon("export_deposit.svg"))
		self.button_export.setIconSize(QtCore.QSize(32, 32))
		self.button_export.clicked.connect(self.on_export)
		self.controls.layout().addWidget(self.button_export)
		
		self.button_import = QtWidgets.QPushButton("Import")
		self.button_import.setIcon(self._vusertools.get_icon("import.svg"))
		self.button_import.setIconSize(QtCore.QSize(32, 32))
		self.button_import.clicked.connect(self.on_import)
		self.controls.layout().addWidget(self.button_import)
		
		self.controls.layout().addStretch()
		
		self.layout().addWidget(self.tool_list)
		self.layout().addWidget(self.controls)
		
		self.populate()
		self.update()
		
		self.tool_list.itemSelectionChanged.connect(self.on_selection_changed)
		
	def start_query_editor(self, query_tool = None):
		
		dialog = EditorQuery(self._vusertools, query_tool)
		dialog.signal_add_tool.connect(lambda user_tool: self._vusertools.signal_add_tool.emit(user_tool))
		dialog.signal_update_tool.connect(lambda label, user_tool: self._vusertools.signal_update_tool.emit(label, user_tool))
		dialog.show()
	
	def start_form_editor(self, form_tool = None, entry = False):
		
		self._vusertools.form_editor = EditorForm(self._vusertools, form_tool, entry)
		self._vusertools.form_editor.signal_add_tool.connect(lambda user_tool: self._vusertools.signal_add_tool.emit(user_tool))
		self._vusertools.form_editor.signal_update_tool.connect(lambda label, user_tool: self._vusertools.signal_update_tool.emit(label, user_tool))
		self._vusertools.form_editor.show()
	
	def stop_form_editor(self):
		
		self._vusertools.form_editor.close()
		self._vusertools.form_editor = None
	
	def populate(self):
		
		self.tool_list.clear()
		for action in self._vusertools._toolbar.actions():
			if not issubclass(action.__class__, UserTool):
				continue
			item = QtWidgets.QListWidgetItem(action.icon(), action.text())
			item._tool = action
			self.tool_list.addItem(item)
	
	def get_selected(self):
		
		return [item._tool for item in self.tool_list.selectedItems()]
	
	def update(self):
		
		selected = self.get_selected()
		self.button_edit.setEnabled(len(selected) == 1)
		self.button_delete.setEnabled(len(selected) > 0)
		self.button_order_up.setEnabled(len(selected) == 1)
		self.button_order_down.setEnabled(len(selected) == 1)
		self.button_export.setEnabled(len(selected) == 1)
	
	@QtCore.Slot()
	def on_edit(self):
		
		tool = self.get_selected()[0]
		if isinstance(tool, Query):
			self.start_query_editor(tool)
		if isinstance(tool, SearchForm):
			self.start_form_editor(tool, entry = False)
		elif isinstance(tool, EntryForm):
			self.start_form_editor(tool, entry = True)
	
	@QtCore.Slot()
	def on_add_query(self):
		
		self.start_query_editor()
	
	@QtCore.Slot()
	def on_add_search(self):
		
		self.start_form_editor(entry = False)
	
	@QtCore.Slot()
	def on_add_entry(self):
		
		self.start_form_editor(entry = True)
	
	@QtCore.Slot()
	def on_delete(self):
		
		labels = [tool.label for tool in self.get_selected()]
		if not labels:
			return
		reply = QtWidgets.QMessageBox.question(self, "Delete Tool", "Delete %d tools?" % (len(labels)), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
		if reply != QtWidgets.QMessageBox.Yes:
			return
		self.signal_del_tool.emit(labels)
	
	@QtCore.Slot()
	def on_order_up(self):
		
		pass
	
	@QtCore.Slot()
	def on_order_down(self):
		
		pass
	
	@QtCore.Slot()
	def on_export(self):
		
		self.signal_export.emit(self.get_selected()[0])
	
	@QtCore.Slot()
	def on_import(self):
		
		self.signal_import.emit()
	
	@QtCore.Slot()
	def on_selection_changed(self):
		
		self.update()
	
	@QtCore.Slot()
	def on_data_changed(self):
		
		self.update()
	
	@QtCore.Slot()
	def on_tools_changed(self):
		
		self.populate()
