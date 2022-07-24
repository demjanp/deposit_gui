from deposit_gui.view.vusertools_elements.user_elements.column_break import (ColumnBreak)

from PySide2 import (QtWidgets)

class EditorColumn(QtWidgets.QFrame):
	
	def __init__(self):
		
		QtWidgets.QFrame.__init__(self)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.setStyleSheet("EditorColumn {border: 1px solid gray;}")
	
	def user_element(self):
		
		return ColumnBreak()
