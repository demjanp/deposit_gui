from deposit_gui.view.vusertools_elements.user_elements.user_element_list import (UserElementList)

from PySide6 import (QtCore)

class EntryForm(UserElementList):
	
	def __init__(self, label, vusertools):
		
		UserElementList.__init__(self, label, vusertools)
		
		self.setIcon(self._vusertools.get_icon("form.svg"))
		self.setToolTip("Entry Form: %s" % self.label)
	
	@QtCore.Slot(bool)
	def on_triggered(self, state):
		
		self._vusertools.open_entry_form(self)
	
