from deposit_gui.dialogs.dialog_connect import DialogConnect

class DialogImportSource(DialogConnect):
	
	def title(self):
		
		return "Select Data Source to Import"
	
	def creating_enabled(self):
		
		return False
	
	def logo(self):
		
		return None