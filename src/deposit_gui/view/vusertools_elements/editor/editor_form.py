from deposit_gui.view.vusertools_elements.editor.editor_frame import (EditorFrame)
from deposit_gui.view.vusertools_elements.editor.editor_group import (EditorGroup)
from deposit_gui.view.vusertools_elements.editor.editor_select import (EditorSelect)
from deposit_gui.view.vusertools_elements.editor.editor_unique import (EditorUnique)
from deposit_gui.view.vusertools_elements.editor.editor_column import (EditorColumn)
from deposit_gui.view.vusertools_elements.editor.editor_actions import (Action)
from deposit_gui.view.vusertools_elements.editor import editor_actions as EditorActions
from deposit_gui.view.vusertools_elements.user_elements.search_form import (SearchForm)
from deposit_gui.view.vusertools_elements.user_elements.entry_form import (EntryForm)
from deposit_gui.view.vusertools_elements.user_elements.user_controls import (UserControl, Select, Unique)
from deposit_gui.view.vusertools_elements.user_elements.column_break import (ColumnBreak)
from deposit_gui.view.vusertools_elements.user_elements.user_groups import (Group)

from PySide6 import (QtWidgets, QtCore)

class EditorForm(QtWidgets.QMainWindow):
	
	signal_add_tool = QtCore.Signal(object)			# form
	signal_update_tool = QtCore.Signal(str, object)	# label, form
	
	def __init__(self, vusertools, form_tool, entry):
		
		QtWidgets.QMainWindow.__init__(self, vusertools.vmain)
		
		self._vusertools = vusertools
		
		self.entry = entry
		self.form_tool = form_tool
		self.columns = []
		
		self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
		
		self.central_widget = QtWidgets.QWidget(self)
		layout = QtWidgets.QVBoxLayout()
		self.central_widget.setLayout(layout)
		self.setCentralWidget(self.central_widget)
		
		self.title_frame = QtWidgets.QFrame()
		title_frame_layout = QtWidgets.QHBoxLayout()
		self.title_frame.setLayout(title_frame_layout)
		self.title_frame.layout().setContentsMargins(0, 0, 0, 0)
		self.title_frame.layout().addWidget(QtWidgets.QLabel("Title:"))
		self.title_edit = QtWidgets.QLineEdit()
		self.title_frame.layout().addWidget(self.title_edit)
		self.central_widget.layout().addWidget(self.title_frame)
		
		self.controls_frame = QtWidgets.QFrame()
		controls_frame_layout = QtWidgets.QHBoxLayout()
		self.controls_frame.setLayout(controls_frame_layout)
		self.controls_frame.layout().setContentsMargins(10, 10, 10, 10)
		
		scroll_area = QtWidgets.QScrollArea()
		scroll_area.setWidgetResizable(True)
		scroll_area.setWidget(self.controls_frame)
		
		self.central_widget.layout().addWidget(scroll_area)
		
		self.selects_frame = QtWidgets.QFrame()
		selects_frame_layout = QtWidgets.QHBoxLayout()
		self.selects_frame.setLayout(selects_frame_layout)
		self.selects_frame.layout().setContentsMargins(10, 10, 10, 10)
		if not self.entry:
			self.selects_frame.layout().addWidget(QtWidgets.QLabel("SELECT"))
			self.selects_frame.layout().addStretch()
		self.central_widget.layout().addWidget(self.selects_frame)
		
		self.unique_frame = QtWidgets.QFrame()
		unique_frame_layout = QtWidgets.QHBoxLayout()
		self.unique_frame.setLayout(unique_frame_layout)
		self.unique_frame.layout().setContentsMargins(10, 10, 10, 10)
		
		button_unique = QtWidgets.QToolButton()
		button_unique.setIcon(self._vusertools.get_icon("add.svg"))
		button_unique.setIconSize(QtCore.QSize(24, 24))
		button_unique.setAutoRaise(True)
		button_unique.setToolTip("Add Class with unique objects")
		button_unique.clicked.connect(self.on_add_unique)
		
		if self.entry:
			self.unique_frame.layout().addWidget(QtWidgets.QLabel("Always add:"))
			self.unique_frame.layout().addWidget(button_unique)
			self.unique_frame.layout().addStretch()
		self.central_widget.layout().addWidget(self.unique_frame)
		
		self.setWindowTitle("Entry Form Editor")
		self.setWindowIcon(self._vusertools.get_icon("form.svg"))
		
		self.toolbar = self.addToolBar("Toolbar")
		self.toolbar.setIconSize(QtCore.QSize(36,36))
		
		for key in EditorActions.__dict__:
			action = getattr(EditorActions, key)
			if not isinstance(action, type):
				continue
			if key.startswith("_Separator"):
				self.toolbar.addSeparator()
				continue
			if (action == Action) or (not issubclass(action, Action)):
				continue
			self.toolbar.addAction(action(self))
		
		button_frame = QtWidgets.QFrame()
		button_frame_layout = QtWidgets.QHBoxLayout()
		button_frame.setLayout(button_frame_layout)
		button_frame.layout().setContentsMargins(5, 5, 5, 5)
		button_frame.layout().addStretch()
		button_save = QtWidgets.QPushButton("Save")
		button_save.clicked.connect(self.on_save)
		button_frame.layout().addWidget(button_save)
		button_cancel = QtWidgets.QPushButton("Cancel")
		button_cancel.clicked.connect(self.on_cancel)
		button_frame.layout().addWidget(button_cancel)
		self.central_widget.layout().addWidget(button_frame)
		
		if self.form_tool is not None:
			self.title_edit.setText(self.form_tool.label)
			for element in self.form_tool.elements:
				if issubclass(element.__class__, Select):
					self.add_select(element)
				elif isinstance(element, Unique):
					self.add_unique(element)
				elif isinstance(element, ColumnBreak):
					self.add_column()
				elif issubclass(element.__class__, UserControl):
					self.add_frame(element.__class__.__name__, element)
				elif issubclass(element.__class__, Group):
					self.add_group(element.__class__.__name__, element)
		
		if not self.columns:
			self.add_column()
		
		self.update_toolbar()
	
	def get_selected(self):
		
		for column in self.columns:
			for element in column.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
				if isinstance(element, EditorGroup) or isinstance(element, EditorFrame):
					if element.selected:
						return element
					if isinstance(element, EditorGroup):
						element = element.get_selected()
						if element is not None:
							return element
		for element in self.selects_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorSelect):
				if element.selected:
					return element
		for element in self.unique_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorUnique):
				if element.selected:
					return element
		return None
	
	def deselect_all(self):
		
		for element in self.controls_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorGroup) or isinstance(element, EditorFrame):
				element.setSelected(False)
				if isinstance(element, EditorGroup):
					element.deselect_all()
		for element in self.selects_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorSelect):
				element.setSelected(False)
		for element in self.unique_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if isinstance(element, EditorUnique):
				element.setSelected(False)
	
	def update_toolbar(self):
		
		selected = self.get_selected()
		for action in self.toolbar.actions():
			if action.isSeparator():
				continue
			action.update()
	
	def get_control_index(self, element):
		
		for column in self.columns:
			idx = column.layout().indexOf(element)
		return column, idx
	
	def add_column(self):
		
		self.columns.append(EditorColumn())
		self.controls_frame.layout().addWidget(self.columns[-1])
	
	def add_frame(self, element, user_control = None):
		
		selected = self.get_selected()
		if isinstance(selected, EditorGroup):
			selected.add_frame(element)
		elif isinstance(selected, EditorFrame):
			if selected.form_editor == self:
				column, idx = self.get_control_index(selected)
				column.layout().insertWidget(idx, EditorFrame(element, self, user_control))
			else:
				selected.form_editor.add_frame(element, before = selected)
		else:
			self.columns[-1].layout().addWidget(EditorFrame(element, self, user_control))
	
	def add_group(self, element, user_group = None):
		
		selected = self.get_selected()
		idx = None
		if (selected is None) or (not isinstance(selected, EditorSelect)):
			if (selected is not None) and (selected.form_editor == self):
				column, idx = self.get_control_index(selected)
		if idx is None:
			self.columns[-1].layout().addWidget(EditorGroup(element, self, user_group))
		else:
			column.layout().insertWidget(idx, EditorGroup(element, self, user_group))
	
	def add_select(self, user_select = None):
		
		selected = self.get_selected()
		if selected is not None:
			idx = self.selects_frame.layout().indexOf(selected)
		else:
			idx = self.selects_frame.layout().count() - 1
		self.selects_frame.layout().insertWidget(idx, EditorSelect(self, user_select))
	
	def add_unique(self, user_unique = None):
		
		selected = self.get_selected()
		if selected is not None:
			idx = self.unique_frame.layout().indexOf(selected)
		else:
			idx = self.unique_frame.layout().count() - 2
		self.unique_frame.layout().insertWidget(idx, EditorUnique(self, user_unique))
	
	def remove_control(self, element):
		
		column, _ = self.get_control_index(element)
		column.layout().removeWidget(element)
	
	def delete(self):
		
		selected = self.get_selected()
		if selected is None:
			return
		if isinstance(selected, EditorFrame):
			selected.form_editor.remove_control(selected)
		elif isinstance(selected, EditorGroup):
			self.remove_control(selected)
		elif isinstance(selected, EditorSelect):
			self.selects_frame.layout().removeWidget(selected)
		elif isinstance(selected, EditorUnique):
			self.unique_frame.layout().removeWidget(selected)
		selected.selected = False
		selected.setParent(None)
		self.update_toolbar()
	
	def save(self):
		
		if self.entry:
			Form = EntryForm
		else:
			Form = SearchForm
		title = self.title_edit.text()
		if title:
			form = Form(title, self._vusertools)
			for column in self.columns:
				form.elements.append(column.user_element())
				for element in column.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
					if element.parent() != column:
						continue
					if isinstance(element, EditorGroup) or isinstance(element, EditorFrame):
						form.elements.append(element.user_element())
			for element in self.selects_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
				if isinstance(element, EditorSelect):
					form.elements.append(element.user_element())
			for element in self.unique_frame.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
				if isinstance(element, EditorUnique):
					form.elements.append(element.user_element())
			if self.form_tool is None:
				self.signal_add_tool.emit(form)
			else:
				self.signal_update_tool.emit(self.form_tool.label, form)
	
	@QtCore.Slot()
	def on_selection_changed(self):
		
		self.update_toolbar()
	
	@QtCore.Slot()
	def on_add_unique(self):
		
		self.add_unique()
	
	@QtCore.Slot()
	def on_save(self):
		
		self.save()
		self.close()
	
	@QtCore.Slot()
	def on_cancel(self):
		
		self.close()

