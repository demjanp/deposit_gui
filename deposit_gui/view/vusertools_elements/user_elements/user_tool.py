
from PySide2 import (QtWidgets, QtCore, QtGui)

class UserTool(QtWidgets.QAction):
	
	def __init__(self, label, vusertools):
		
		self.label = label
		self._vusertools = vusertools
		
		QtWidgets.QAction.__init__(self, self._vusertools.vmain)
		
		self.setText(self.label)
		self.triggered.connect(self.on_triggered)
	
	@QtCore.Slot(bool)
	def on_triggered(self, state):
		
		pass
	
	def to_markup(self):
		
		return '''
<Title>%s</>
<Type %s/>
		''' % (self.label, self.__class__.__name__)
	
	def to_dict(self):
		
		return dict(
			typ = self.__class__.__name__,
			label = self.label,
		)

