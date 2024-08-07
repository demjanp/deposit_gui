from deposit_gui.view.vusertools_elements.user_elements.user_element import (UserElement)

class UserUnique(UserElement):
	
	def __init__(self, dclass):
		
		self.dclass = dclass
		
		UserElement.__init__(self)
	
	def to_dict(self):
		
		return dict(
			dclass = self.dclass,
			**UserElement.to_dict(self),
		)

