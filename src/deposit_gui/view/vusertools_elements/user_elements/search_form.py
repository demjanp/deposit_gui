from deposit_gui.view.vusertools_elements.user_elements.user_element_list import (UserElementList)

from PySide6 import (QtCore)

class SearchForm(UserElementList):
	
	def __init__(self, label, vusertools):
		
		UserElementList.__init__(self, label, vusertools)
		
		self.setIcon(self._vusertools.get_icon("search.svg"))
		self.setToolTip("Search Form: %s" % self.label)
	
	@QtCore.Slot(bool)
	def on_triggered(self, state):
		
		self._vusertools.open_search_form(self)
	
