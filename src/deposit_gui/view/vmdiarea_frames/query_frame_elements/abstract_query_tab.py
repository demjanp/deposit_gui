class AbstractQueryTab(object):
	
	def update_query(self, *args, **kwargs):
		
		pass
	
	def apply_filter(self, *args, **kwargs):
		
		pass
	
	def get_row_count(self):
		
		return 0
	
	def on_close(self):
		
		pass
	
	def on_selected(self):
		
		pass
