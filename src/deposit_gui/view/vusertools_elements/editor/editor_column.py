from deposit_gui.view.vusertools_elements.user_elements.column_break import (ColumnBreak)

from PySide6 import (QtWidgets)

class EditorColumn(QtWidgets.QFrame):
	
	def __init__(self):
		
		QtWidgets.QFrame.__init__(self)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.setStyleSheet("EditorColumn {border: 1px solid gray;}")
	
	def user_element(self):
		
		return ColumnBreak()
