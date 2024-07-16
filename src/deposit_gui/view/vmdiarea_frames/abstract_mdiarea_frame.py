from deposit_gui.dgui.abstract_subview import AbstractSubview

class AbstractMDIAreaFrame(AbstractSubview):
	
	def __init__(self):
		
		AbstractSubview.__init__(self)
	
	def title(self):
		# re-implement
		
		return "MDIAreaFrame"
	
	def icon(self):
		# re-implement
		
		return "dep_cube.svg"
	
	def on_close(self):
		# re-implement
		
		pass
	
	def on_deactivate(self):
		# re-implement
		
		pass
