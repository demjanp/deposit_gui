from PySide6 import (QtWidgets, QtCore, QtGui)

class DDialog(QtWidgets.QDialog):
	
	signal_process = QtCore.Signal(str, object)
	signal_cancel = QtCore.Signal(str, object)
	
	def __init__(self, name, view):

		QtWidgets.QDialog.__init__(self, view)
		
		self._name = name
		self._frame = None
		self._data = None
		self._args = []
		self._kwargs = {}
		self._button_box = None


		self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.setWindowFlags(self.windowFlags() |  QtCore.Qt.WindowStaysOnTopHint)
		
		self.accepted.connect(self.on_accepted)
		self.rejected.connect(self.on_rejected)
	
	def set_title(self, name):
		
		self.setWindowTitle(name)
	
	def set_frame(self, frame):
		
		self._frame = frame
		self.setLayout(self._frame.layout())
	
	def get_frame(self):
		
		return self._frame
	
	def set_data(self, data):
		
		self._data = data
	
	def get_data(self):
		
		return self._data
	
	def set_button_box(self, ok, cancel):
		
		if not (ok or cancel):
			return
		if ok and cancel:
			flags = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
		elif ok:
			flags = QtWidgets.QDialogButtonBox.Ok
		else:
			flags = QtWidgets.QDialogButtonBox.Cancel
		self._button_box = QtWidgets.QFrame()
		layout = QtWidgets.QVBoxLayout()
		self._button_box.setLayout(layout)
		buttons = QtWidgets.QDialogButtonBox(flags, QtCore.Qt.Horizontal)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)
		self._button_box.layout().addWidget(buttons)
	
	def set_enabled(self, state):
		
		if self._button_box is not None:
			self._button_box.layout().itemAt(0).widget().button(QtWidgets.QDialogButtonBox.Ok).setEnabled(state)
	
	@QtCore.Slot()
	def on_accepted(self):
		
		self.signal_process.emit(self._name, self)
	
	@QtCore.Slot()
	def on_rejected(self):
		
		self.signal_cancel.emit(self._name, self)
	
