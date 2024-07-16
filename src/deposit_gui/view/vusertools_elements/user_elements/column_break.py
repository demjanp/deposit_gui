from deposit_gui.view.vusertools_elements.user_elements.user_element import (UserElement)

class ColumnBreak(UserElement):
	
	def __init__(self):
		
		UserElement.__init__(self)
	
	def to_markup(self):
		
		return "<ColumnBreak/>"
