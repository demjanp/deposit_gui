from deposit_gui.view.vusertools_elements.user_elements.user_element import (UserElement)

class UserLabeledElement(UserElement):
	
	def __init__(self, stylesheet, label):
		
		self.stylesheet = stylesheet
		self.label = label
		
		UserElement.__init__(self)
	
	def to_dict(self):
		
		return dict(
			stylesheet = self.stylesheet,
			label = self.label,
			**UserElement.to_dict(self),
		)

