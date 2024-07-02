from deposit_gui.view.vusertools_elements.user_elements.user_tool import (UserTool)

from PySide6 import (QtCore)

class Query(UserTool):
	
	def __init__(self, label, value, vusertools):
		
		self.value = value
		
		UserTool.__init__(self, label, vusertools)
		
		self.setIcon(self._vusertools.get_icon("query.svg"))
		self.setToolTip("Query: %s" % self.label)
		
		self._vusertools._cmodel.cmain.signal_selection_changed.connect(self.update)
		
		self.update()
	
	@QtCore.Slot()
	def update(self):
		
		if self._vusertools is None:
			return
		if (self._vusertools.SELECTED_STR not in self.value) or (self._vusertools.get_selected_id() is not None):
			self.setEnabled(True)
		else:
			self.setEnabled(False)
	
	@QtCore.Slot(bool)
	def on_triggered(self, state):
		
		self._vusertools.open_query(self)
	
	def to_markup(self):
		
		return UserTool.to_markup(self) + '''
<QueryString>%s</>
		''' % (self.value)
	
	def to_dict(self):
		
		return dict(
			value = self.value,
			**UserTool.to_dict(self),
		)

