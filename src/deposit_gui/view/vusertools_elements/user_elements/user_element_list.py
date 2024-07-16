from deposit_gui.view.vusertools_elements.user_elements.user_tool import (UserTool)

class UserElementList(UserTool):
	
	def __init__(self, label, vusertools):
		
		self.elements = []
		UserTool.__init__(self, label, vusertools)
	
	def to_markup(self):
		
		return UserTool.to_markup(self) + "\n".join([element.to_markup() for element in self.elements])
	
	def to_dict(self):
		
		return dict(
			elements = [element.to_dict() for element in self.elements],
			**UserTool.to_dict(self),
		)
