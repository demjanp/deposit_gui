from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.view.vquerytoolbar import VQueryToolbar

from PySide2 import (QtCore)

class CQueryToolbar(AbstractSubcontroller):
	
	def __init__(self, cmain, cview) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vquerytoolbar = VQueryToolbar(cview._view)
		
		self._vquerytoolbar.signal_entered.connect(self.on_query_entered)
	
	def set_query_text(self, text):
		
		self._vquerytoolbar.set_query_text(text)
	
	def get_query_text(self):
		
		return self._vquerytoolbar.get_query_text()
	
	@QtCore.Slot(str)
	def on_query_entered(self, querystr):
		
		self.cmain.cmdiarea.add_query(querystr)

