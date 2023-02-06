from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.view.vusertools_elements.user_elements.search_form import (SearchForm)
from deposit_gui.view.vusertools_elements.user_elements.entry_form import (EntryForm)
from deposit_gui.view.vusertools_elements.user_elements.query import (Query)
from deposit_gui.view.vusertools_elements.user_elements import user_controls as UserControls
from deposit_gui.view.vusertools_elements.user_elements import user_groups as UserGroups
from deposit_gui.view.vusertools_elements.user_elements.column_break import (ColumnBreak)
from deposit_gui.view.vusertools_elements.manager import (Manager)
from deposit_gui.view.vusertools_elements.dialog.dialog_search_form import (DialogSearchForm)
from deposit_gui.view.vusertools_elements.dialog.dialog_entry_form import (DialogEntryForm)

from PySide2 import (QtWidgets, QtCore, QtGui)

class VUserTools(AbstractSubview):
	
	signal_search_submit = QtCore.Signal(str)
	#	querystr
	signal_entry_submit = QtCore.Signal(dict, dict, list, set, dict)
	#	values, objects_existing, relations, unique, objects_loaded
	signal_entry_unlink = QtCore.Signal(dict, list, set, list)
	#	objects_existing, relations, unique, obj_ids
	signal_entry_remove = QtCore.Signal(dict, set)
	#	objects_existing, unique
	signal_import_tool = QtCore.Signal()
	signal_export_tool = QtCore.Signal(object)		# user_tool
	signal_add_tool = QtCore.Signal(object)			# user_tool
	signal_update_tool = QtCore.Signal(str, object)	# label, user_tool
	signal_del_tool = QtCore.Signal(list)			# [label, ...]
	
	signal_data_changed = QtCore.Signal()  # internal signal
	signal_tools_changed = QtCore.Signal()  # internal signal
	
	SELECTED_STR = "{selected}"
	
	def __init__(self, vmain, cmodel) -> None:
		
		AbstractSubview.__init__(self, vmain)
		
		self._cmodel = cmodel
		
		self.vmain.addToolBarBreak()
		self._toolbar = self.vmain.addToolBar("User Tools")
		self._manager = None
		self._form_editor = None
		self.entry_form_geometry = None
		
		self._toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
		
		self.action_manage = QtWidgets.QAction("User Tools")
		self.action_manage.setToolTip("Manage User Tools")
		self.action_manage.triggered.connect(self.on_manage)
	
	def populate_tools(self, user_tools):
		
		self._toolbar.clear()
		self._toolbar.addAction(self.action_manage)
		self._toolbar.addSeparator()
		for data in user_tools:
			user_tool = self.user_tool_from_dict(data)
			if user_tool is not None:
				self._toolbar.addAction(user_tool)
		self.signal_tools_changed.emit()
	
	def user_tool_from_dict(self, data):
		
		user_tool = None
		if data["typ"] == "Query":
			return Query(data["label"], data["value"], self)
		else:
			typ = None
			if data["typ"] == "SearchForm":
				typ = SearchForm
			elif data["typ"] == "EntryForm":
				typ = EntryForm
			if typ is not None:
				user_tool = typ(data["label"], self)
				if typ in [SearchForm, EntryForm]:
					for element in data["elements"]:
						if element["typ"] in ["Group", "MultiGroup"]:
							user_tool.elements.append(getattr(UserGroups, element["typ"])(element["stylesheet"], element["label"]))
							for member in element["members"]:
								user_tool.elements[-1].members.append(getattr(UserControls, member["typ"])(member["stylesheet"], member["label"], member["dclass"], member["descriptor"]))
						elif element["typ"] == "ColumnBreak":
							user_tool.elements.append(ColumnBreak())
						elif element["typ"] == "Unique":
							user_tool.elements.append(getattr(UserControls, element["typ"])(element["stylesheet"], element["label"], element["dclass"]))
						else:
							user_tool.elements.append(getattr(UserControls, element["typ"])(element["stylesheet"], element["label"], element["dclass"], element["descriptor"]))
				return user_tool
		return None
	
	def start_manager(self):
		
		self._manager = Manager(self)
		self._manager.signal_export.connect(lambda user_tool: self.signal_export_tool.emit(user_tool))
		self._manager.signal_import.connect(lambda: self.signal_import_tool.emit())
		self._manager.signal_del_tool.connect(lambda labels: self.signal_del_tool.emit(labels))
		self.signal_data_changed.connect(self._manager.on_data_changed)
		self.signal_tools_changed.connect(self._manager.on_tools_changed)
		self._manager.show()
	
	def get_selected_id(self):
		
		objects = self._cmodel.cmain.get_selected_objects()
		if len(objects) == 1:
			return list(objects)[0].id
		
		rows = set()
		for item in self._cmodel.cmain.get_selected_queryitems():
			rows.add(item.row)
		if len(rows) == 1:
			return item.obj_id_row
		
		return None
	
	def open_query(self, form_tool):
		
		querystr = form_tool.value
		id = str(self.get_selected_id())
		while self.SELECTED_STR in querystr:
			idx1 = querystr.lower().find(self.SELECTED_STR)
			idx2 = idx1 + len(self.SELECTED_STR)
			querystr = querystr[:idx1] + id + querystr[idx2:]
		self.signal_search_submit.emit(querystr)
	
	def open_search_form(self, form_tool):
		
		dialog = DialogSearchForm(self, form_tool)
		dialog.signal_submit.connect(lambda querystr: self.signal_search_submit.emit(querystr))
		self.signal_data_changed.connect(dialog.on_data_changed)
		dialog.update_lookups()
		dialog.show()
	
	def open_entry_form(self, form_tool):
		
		dialog = DialogEntryForm(self, form_tool, self.get_selected_id())
		dialog.signal_submit.connect(
			lambda values, objects_existing, relations, unique, objects_loaded: self.signal_entry_submit.emit(
				values, objects_existing, relations, unique, objects_loaded
			)
		)
		dialog.signal_unlink.connect(
			lambda objects_existing, relations, unique, obj_ids: self.signal_entry_unlink.emit(
				objects_existing, relations, unique, obj_ids
			)
		)
		dialog.signal_remove.connect(lambda objects_existing, unique: self.signal_entry_remove.emit(
				objects_existing, unique
			)
		)
		self.signal_data_changed.connect(dialog.on_data_changed)
		dialog.update_lookups()
		dialog.show()
	
	@QtCore.Slot()
	def on_manage(self):
		
		self.start_manager()
	
	@QtCore.Slot()
	def on_data_changed(self):
		
		self.signal_data_changed.emit()
	
	@QtCore.Slot()
	def on_close(self):
		
		if self._form_editor is not None:
			self._form_editor.close()
