from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.dgui.ddialog import DDialog

from PySide2 import (QtWidgets, QtCore, QtGui)

class DVDialogs(AbstractSubview):
	
	signal_process = QtCore.Signal(str, object)
	signal_cancel = QtCore.Signal(str, object)
	
	def __init__(self, vmain) -> None:
		
		AbstractSubview.__init__(self, vmain)
	
	def open(self, name):
		
		dialog = DDialog(name, self.vmain.get_active_window())
		
		dialog.signal_process.connect(self.on_process)
		dialog.signal_cancel.connect(self.on_cancel)
		
		return dialog
	
	@QtCore.Slot(str, object)
	def on_process(self, name, dialog):
		
		self.signal_process.emit(name, dialog)
	
	@QtCore.Slot(str, object)
	def on_cancel(self, name, dialog):
		
		self.signal_cancel.emit(name, dialog)
