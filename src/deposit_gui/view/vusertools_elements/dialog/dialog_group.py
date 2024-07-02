from deposit_gui.view.vusertools_elements.dialog.dialog_frame import (DialogFrame)

from PySide6 import (QtWidgets, QtCore)
from natsort import (natsorted)

class DialogGroup(QtWidgets.QGroupBox):
	
	entry_removed = QtCore.Signal(list) # [obj_id, ...]
	
	def __init__(self, cmodel, user_group):
		# user_group = Group
		
		self._cmodel = cmodel
		self.user_group = user_group
		self.controls_frame = None
		
		QtWidgets.QGroupBox.__init__(self, self.user_group.label)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.controls_frame = QtWidgets.QFrame()
		controls_frame_layout = QtWidgets.QVBoxLayout()
		self.controls_frame.setLayout(controls_frame_layout)
		self.controls_frame.layout().setContentsMargins(10, 10, 10, 10)
		self.layout().addWidget(self.controls_frame)
		
		self.lookup_combo = LookupCombo()
		self.lookup_combo_search = {} # {index: {column: value, ...}}
		lookup_button = QtWidgets.QPushButton("Fill")
		lookup_button.clicked.connect(self.on_lookup_combo)
		
		lookup_frame = QtWidgets.QFrame()
		lookup_frame_layout = QtWidgets.QHBoxLayout()
		lookup_frame.setLayout(lookup_frame_layout)
		lookup_frame.layout().setContentsMargins(0, 0, 0, 0)
		lookup_frame.layout().addStretch()
		lookup_frame.layout().addWidget(self.lookup_combo)
		lookup_frame.layout().addWidget(lookup_button)
		self.controls_frame.layout().addWidget(lookup_frame)
		
		for member in self.user_group.members:
			self.add_frame(member)
		
		button_frame = QtWidgets.QWidget()
		button_frame_layout = QtWidgets.QHBoxLayout()
		button_frame.setLayout(button_frame_layout)
		button_frame.layout().setContentsMargins(0, 0, 0, 0)
		button_remove = QtWidgets.QPushButton("Remove")
		button_remove.clicked.connect(self.on_remove)
		button_frame.layout().addStretch()
		button_frame.layout().addWidget(button_remove)
		self.controls_frame.layout().addWidget(button_frame)
		
		self.populate_lookup()
		
		if self.user_group.stylesheet:
			self.setStyleSheet(self.user_group.stylesheet)
	
	def add_frame(self, user_control):
		
		frame = DialogFrame(self._cmodel, user_control)
		frame.ctrl.changed.connect(self.on_ctrl_changed)
		self.controls_frame.layout().addWidget(frame)
	
	def populate_lookup(self):
		
		def str_or_empty(value):
			
			if value is None:
				return ""
			return str(value)
		
		self.lookup_combo.clear()
		self.lookup_combo_search = {} # {index: {column: value, ...}}
		columns = [(member.dclass, member.descriptor) for member in self.user_group.members]
		query = self._cmodel.get_query("SELECT %s" % (", ".join(["[%s].[%s]" % (column) for column in columns])), silent = True)
		rows = []
		for row in range(len(query)):
			data = dict([("[%s].[%s]" % (cls, descr), str_or_empty(query[row, cls, descr][1])) for cls, descr in columns])
			label = ", ".join(list(data.values()))
			row = [label, data]
			if row not in rows:
				rows.append(row)
		rows = natsorted(rows, key = lambda row: row[0])
		index = 0
		for label, data in rows:
			self.lookup_combo_search[index] = data
			index += 1
			self.lookup_combo.addItem(label, data)
	
	def remove(self):
		
		obj_ids = set([])
		for frame in self.frames():
			obj_id = frame.ctrl.obj_id
			if obj_id is not None:
				obj_ids.add(obj_id)
			frame.set_value("", None)
		return list(obj_ids)
	
	def set_data(self, data):
		# data = {Class.Descriptor: value, ...}
		
		for frame in self.frames():
			column = "[%s].[%s]" % (frame.user_control.dclass, frame.user_control.descriptor)
			if column in data:
				frame.set_value(data[column])
	
	def update_lookup_combo(self):
		
		def _find_index(data):
			
			for index in self.lookup_combo_search:
				found = True
				for column in data:
					if column not in self.lookup_combo_search[index]:
						found = False
						break
					if self.lookup_combo_search[index][column] != data[column]:
						found = False
						break
				if found:
					return index
			return None
		
		data = {}
		for frame in self.frames():
			value = frame.get_value()
			if value != "":
				column = "[%s].[%s]" % (frame.user_control.dclass, frame.user_control.descriptor)
				data[column] = value
		if not data:
			return
		index = _find_index(data)
		if index is None:
			return
		self.lookup_combo.setCurrentIndex(index)
	
	def frames(self):
		
		return list(self.controls_frame.findChildren(DialogFrame, options = QtCore.Qt.FindDirectChildrenOnly))
	
	@QtCore.Slot()
	def on_ctrl_changed(self):
		
		self.update_lookup_combo()
	
	@QtCore.Slot()
	def on_lookup_combo(self):
		
		data = self.lookup_combo.currentData()
		if data is None:
			return
		self.set_data(data)
	
	@QtCore.Slot()
	def on_remove(self):
		
		obj_ids = self.remove()
		self.entry_removed.emit(obj_ids)

class LookupCombo(QtWidgets.QComboBox):
	
	def wheelEvent(self, event):
		
		pass

