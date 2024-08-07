from deposit_gui.view.vusertools_elements.user_elements.user_labeled_element import (UserLabeledElement)

class Group(UserLabeledElement):
	
	def __init__(self, stylesheet, label):
		
		self.members = []
		UserLabeledElement.__init__(self, stylesheet, label)
	
	def to_markup(self):
		
		return "<%s style=\"%s\">%s\n" % (self.__class__.__name__, self.stylesheet, self.label) + "\n".join(["\t%s" % (member.to_markup()) for member in self.members]) + "\n</>"
	
	def to_dict(self):
		
		return dict(
			members = [member.to_dict() for member in self.members],
			**UserLabeledElement.to_dict(self),
		)

class MultiGroup(Group):
	
	def __init__(self, stylesheet, label):
		
		Group.__init__(self, stylesheet, label)

