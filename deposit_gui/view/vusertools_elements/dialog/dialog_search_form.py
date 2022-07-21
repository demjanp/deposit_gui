from deposit_gui.view.vusertools_elements.dialog.dialog_form import (DialogForm)

from PySide2 import (QtCore)

class DialogSearchForm(DialogForm):
	
	signal_submit = QtCore.Signal(str)	# querystr
	
	def __init__(self, vusertools, form_tool):
		
		self.selects = []
		
		DialogForm.__init__(self, vusertools, form_tool)
		
		self.setMinimumWidth(600)
	
	def submit(self):
		
		def value_to_str(value):
			
			try:
				value = float(value)
				if value - int(value) == 0:
					value = int(value)
			except:
				value = str(value)
			if isinstance(value, str):
				return "'%s'" % (value)
			return "%s" % str(value)
		
		conditions = []
		frames, _ = self.frames()
		for frame in frames:
			value = frame.get_value()
			if value:
				conditions.append("([%s].[%s] == %s)" % (frame.dclass, frame.descriptor, value_to_str(value)))
				if [frame.dclass, frame.descriptor] not in self.selects:
					self.selects.append([frame.dclass, frame.descriptor])
		
		querystr = "SELECT %s" % (", ".join(["[%s].[%s]" % tuple(select) for select in self.selects]))
		if conditions:
			querystr += " WHERE %s" % (" and ".join(conditions))
		self.signal_submit.emit(querystr)
	
	def clear(self):
		
		frames, _ = self.frames()
		for frame in frames:
			frame.set_value("")
	
	@QtCore.Slot()
	def on_submit(self):
		
		self.submit()
		self.hide()
	
	@QtCore.Slot()
	def on_reset(self):
		
		self.clear()

