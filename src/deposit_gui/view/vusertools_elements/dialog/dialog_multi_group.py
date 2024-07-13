from deposit_gui.view.vusertools_elements.dialog.dialog_frame import (DialogFrame)

from PySide6 import (QtWidgets, QtCore)

class DialogMultiGroup(QtWidgets.QGroupBox):
	
	entry_added = QtCore.Signal()
	entry_removed = QtCore.Signal(list) # [obj_id, ...]
	
	def __init__(self, cmodel, user_group):
		# user_group = MultiGroup
		
		self._cmodel = cmodel
		self.user_group = user_group
		self.controls_frame = None
		self._framesets = []
		
		QtWidgets.QGroupBox.__init__(self, self.user_group.label)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.controls_frame = QtWidgets.QFrame()
		controls_frame_layout = QtWidgets.QVBoxLayout()
		self.controls_frame.setLayout(controls_frame_layout)
		self.controls_frame.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().addWidget(self.controls_frame)
		
		button_frame = QtWidgets.QFrame()
		button_frame_layout = QtWidgets.QHBoxLayout()
		button_frame.setLayout(button_frame_layout)
		button_frame.layout().setContentsMargins(5, 5, 5, 5)
		button_frame.layout().addStretch()
		button_add = QtWidgets.QPushButton("Add Entry")
		button_add.clicked.connect(self.on_add_entry)
		button_frame.layout().addWidget(button_add)
		self.layout().addWidget(button_frame)
		
		self.add_entry()
		
		if self.user_group.stylesheet:
			self.setStyleSheet(self.user_group.stylesheet)
	
	def add_frameset(self):
		
		self._framesets.append(QtWidgets.QFrame())
		layout = QtWidgets.QVBoxLayout()
		self._framesets[-1].setLayout(layout)
		self.controls_frame.layout().addWidget(self._framesets[-1])
		return self._framesets[-1]
	
	def framesets(self):
		# returns [[DialogFrame, ...], ...]
		
		return [list(frameset.findChildren(DialogFrame, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly)) for frameset in self._framesets]
	
	def add_frame(self, user_control):
		
		self._framesets[-1].layout().addWidget(DialogFrame(self._cmodel, user_control))
	
	def add_entry(self):
		
		if len(self._framesets) > 0:
			line = QtWidgets.QFrame()
			line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
			line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
			self.controls_frame.layout().addWidget(line)
		self.add_frameset()
		for member in self.user_group.members:
			self.add_frame(member)
		
		button_frame = QtWidgets.QWidget()
		button_frame_layout = QtWidgets.QHBoxLayout()
		button_frame.setLayout(button_frame_layout)
		button_frame.layout().setContentsMargins(0, 0, 0, 0)
		button_remove = QtWidgets.QPushButton("Remove")
		button_remove.clicked.connect(self.on_remove_entry)
		button_frame.layout().addStretch()
		button_frame.layout().addWidget(button_remove)
		self._framesets[-1].layout().addWidget(button_frame)
		
		return list(self._framesets[-1].findChildren(DialogFrame, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly))
	
	def remove_entry(self, frameset):
		
		for idx, frm in enumerate(self._framesets):
			if frm == frameset:
				break
		
		obj_ids = set([])
		for frame in self._framesets[idx].findChildren(DialogFrame, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			obj_id = frame.ctrl.obj_id
			if obj_id is not None:
				obj_ids.add(obj_id)
			frame.set_value("", None)
		
		if idx > 0:
			
			# remove HLine after frameset
			idx_layout = self.controls_frame.layout().indexOf(frameset)
			line = self.controls_frame.layout().itemAt(idx_layout + 1)
			if line is not None:
				line = line.widget()
				self.controls_frame.layout().removeWidget(line)
				line.setParent(None)
			
			self.controls_frame.layout().removeWidget(frameset)
			frameset.setParent(None)
			del self._framesets[idx]
		
		return list(obj_ids)
	
	def clear(self):
		
		for frame in self.controls_frame.findChildren(QtWidgets.QFrame, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly):
			if frame.__class__.__name__ != "QFrame":
				continue
			self.controls_frame.layout().removeWidget(frame)
			frame.setParent(None)
		self._framesets = []
		self.add_entry()
	
	@QtCore.Slot()
	def on_add_entry(self):
	
		self.add_entry()
		self.entry_added.emit()
	
	@QtCore.Slot()
	def on_remove_entry(self):
		
		obj_ids = self.remove_entry(self.sender().parent().parent())
		self.entry_removed.emit(obj_ids)
		
