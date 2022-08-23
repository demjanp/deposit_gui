from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.dgui.dvdialogs import DVDialogs

from PySide2 import (QtWidgets, QtCore, QtGui)

class DCDialogs(AbstractSubcontroller):
	
	def __init__(self, cmain, cview) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vdialogs = DVDialogs(cview._view)
		self._dialogs = {}
		
		self._vdialogs.signal_process.connect(self.on_dialog_process)
		self._vdialogs.signal_cancel.connect(self.on_dialog_cancel)
	
	def open(self, name, *args, **kwargs):
		
		if name in self._dialogs:
			self._dialogs[name].close()
			del self._dialogs[name]
		
		dialog = self._vdialogs.open(name)
		dialog._args = args
		dialog._kwargs = kwargs
		
		if hasattr(self, "set_up_%s" % (name)):
			getattr(self, "set_up_%s" % (name))(dialog, *args, **kwargs)
			if dialog._button_box is not None:
				dialog.layout().addWidget(dialog._button_box)
			dialog.adjustSize()
		
		dialog.show()
		self._dialogs[name] = dialog
	
	def close(self, name):
		
		if name in self._dialogs:
			self._dialogs[name].close()
	
	def is_open(self, name):
		
		return (name in self._dialogs) and (self._dialogs[name].isVisible())
	
	@QtCore.Slot(str, object)
	def on_dialog_process(self, name, dialog):
		
		if hasattr(self, "process_%s" % (name)):
			getattr(self, "process_%s" % (name))(dialog, *dialog._args, **dialog._kwargs)
		dialog.close()
		if name in self._dialogs:
			del self._dialogs[name]
	
	@QtCore.Slot(str, object)
	def on_dialog_cancel(self, name, dialog):
		
		if hasattr(self, "cancel_%s" % (name)):
			getattr(self, "cancel_%s" % (name))(dialog, *dialog._args, **dialog._kwargs)
		dialog.close()
		if name in self._dialogs:
			del self._dialogs[name]
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	
	# ---- Dialogs
	# ------------------------------------------------------------------------
	'''
	Implement set_up_[name], process_[name] and cancel_[name] for each dialog:
	
	def set_up_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		dialog = QtWidgets.QDialog
		
		dialog.set_title(name)
		dialog.set_frame(frame = QtWidget)
		dialog.get_frame()
		dialog.set_button_box(ok: bool, cancel: bool): set if OK and Cancel buttons are visible
		
	def process_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		process dialog after OK has been clicked
	
	def cancel_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		handle dialog after cancel has been clicked
	'''
