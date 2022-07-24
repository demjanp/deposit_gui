from deposit_gui.view.vusertools_elements.dialog.dialog_column import (DialogColumn)
from deposit_gui.view.vusertools_elements.dialog.dialog_frame import (DialogFrame)
from deposit_gui.view.vusertools_elements.dialog.dialog_group import (DialogGroup)
from deposit_gui.view.vusertools_elements.dialog.dialog_multi_group import (DialogMultiGroup)
from deposit_gui.view.vusertools_elements.user_elements.user_groups import (Group, MultiGroup)
from deposit_gui.view.vusertools_elements.user_elements.user_controls import (UserControl, Select, Unique)
from deposit_gui.view.vusertools_elements.user_elements.column_break import (ColumnBreak)

from PySide2 import (QtWidgets, QtCore)

class DialogForm(QtWidgets.QDialog):

	def __init__(self, vusertools, form_tool):
		
		QtWidgets.QDialog.__init__(self, vusertools.vmain)
		
		self._vusertools = vusertools
		
		self.form_tool = form_tool
		self.buttonBox = None
		self.columns = []  # [DialogColumn(), ...]
		self.selects = []  # [[class, descriptor], ...]
		self.unique = set()  # {class, ...}
		
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		
		self.setWindowTitle(self.form_tool.label)
		self.setModal(False)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.controls_frame = QtWidgets.QFrame()
		self.controls_frame.setLayout(QtWidgets.QGridLayout())
		self.controls_frame.layout().setContentsMargins(10, 10, 10, 10)
		
		self.scroll_area = VerticalScrollArea(self.controls_frame)
		
		self.layout().addWidget(self.scroll_area)
		
		self.button_frame = QtWidgets.QFrame()
		self.button_frame.setLayout(QtWidgets.QHBoxLayout())
		self.button_frame.layout().setContentsMargins(5, 5, 5, 5)
		self.button_frame.layout().addStretch()
		button_submit = QtWidgets.QPushButton("Submit")
		button_submit.clicked.connect(self.on_submit)
		self.button_frame.layout().addWidget(button_submit)
		button_reset = QtWidgets.QPushButton("Reset")
		button_reset.clicked.connect(self.on_reset)
		self.button_frame.layout().addWidget(button_reset)
		self.layout().addWidget(self.button_frame)
		
		for element in self.form_tool.elements:
			if issubclass(element.__class__, Select):
				self.add_select(element)
			elif isinstance(element, Unique):
				self.add_unique(element)
			elif isinstance(element, ColumnBreak):
				self.add_column()
			elif issubclass(element.__class__, UserControl):
				self.add_frame(element)
			elif issubclass(element.__class__, Group):
				self.add_group(element)
		
		self.adjust_labels()
	
	def set_enabled(self, state):
		
		if self.buttonBox is not None:
			self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(state)
	
	def add_column(self):
		
		self.columns.append(DialogColumn())
		self.controls_frame.layout().addWidget(self.columns[-1], 0, len(self.columns) - 1)
	
	def add_frame(self, user_control):
		
		self.columns[-1].add_widget(DialogFrame(self._vusertools._cmodel, user_control))
	
	def add_group(self, user_group):
		
		dialog_group = None
		if isinstance(user_group, MultiGroup):
			dialog_group = DialogMultiGroup(self._vusertools._cmodel, user_group)
			dialog_group.entry_added.connect(self.on_entry_added)
			dialog_group.entry_removed.connect(self.on_entry_removed)
		elif isinstance(user_group, Group):
			dialog_group = DialogGroup(self._vusertools._cmodel, user_group)
			dialog_group.entry_removed.connect(self.on_entry_removed)
		if dialog_group is None:
			return
		self.columns[-1].add_widget(dialog_group)
	
	def add_select(self, user_select):
	
		self.selects.append([user_select.dclass, user_select.descriptor])
	
	def add_unique(self, user_unique):
		
		self.unique.add(user_unique.dclass)
	
	def multigroups(self):
		# returns [DialogMultiGroup(), ...]
		
		groups = []
		for column in self.columns:
			for group in column.findChildren(DialogMultiGroup, options = QtCore.Qt.FindDirectChildrenOnly):
				groups.append(group)
		return groups
	
	def frames(self):
		# returns frames, framesets
		# frames = [DialogFrame(), ...]
		# framesets = [[DialogFrame(), ...], ...]
		
		frames, framesets = [], []
		for column in self.columns:
			for element in column.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindDirectChildrenOnly):
				if isinstance(element, DialogGroup):
					frames += element.frames()
				elif isinstance(element, DialogMultiGroup):
					framesets += element.framesets()
				elif isinstance(element, DialogFrame):
					frames.append(element)
		return frames, framesets
	
	def adjust_labels(self):
		
		for column in self.columns:
			wmax = 0
			for label in column.findChildren(QtWidgets.QLabel):
				wmax = max(wmax, label.sizeHint().width())
			for label in column.findChildren(QtWidgets.QLabel):
				label.setFixedWidth(wmax)
				label.setAlignment(QtCore.Qt.AlignRight)
	
	def update_lookups(self):
		
		for column in self.columns:
			for element in column.findChildren(QtWidgets.QWidget):
				if isinstance(element, DialogGroup) or isinstance(element, DialogFrame):
					element.populate_lookup()
	
	def sizeHint(self):
		
		margins = self.controls_frame.layout().contentsMargins()
		w = self.controls_frame.sizeHint().width() + self.scroll_area.verticalScrollBar().width() + margins.left() + margins.right()
		h = self.controls_frame.sizeHint().height() + self.button_frame.sizeHint().height() + margins.top() + margins.bottom()
		return QtCore.QSize(w, h)
	
	def resizeEvent(self, event):
		
		if not self.columns:
			return
		w = 0
		for column in self.columns:
			w += column.sizeHint().width()
		w = int(round(w / len(self.columns)))
		for col in range(len(self.columns)):
			self.controls_frame.layout().setColumnMinimumWidth(col, w)
	
	@QtCore.Slot()
	def on_entry_added(self):
		
		self.adjust_labels()
	
	@QtCore.Slot(list)
	def on_entry_removed(self, obj_ids):
		
		pass
	
	@QtCore.Slot()
	def on_submit(self):
		
		pass
	
	@QtCore.Slot()
	def on_reset(self):
		
		pass
	
	@QtCore.Slot()
	def on_data_changed(self):
		
		self.update_lookups()

class VerticalScrollArea(QtWidgets.QScrollArea):
	
	def __init__(self, contents):
		
		self.contents = contents
		
		QtWidgets.QScrollArea.__init__(self)
		
		self.setWidgetResizable(True)
		self.setFrameStyle(QtWidgets.QFrame.NoFrame)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.contents.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
		self.setWidget(self.contents)
	
	def resizeEvent(self, event):
		
		self.contents.setMinimumWidth(self.width() - self.verticalScrollBar().width())

