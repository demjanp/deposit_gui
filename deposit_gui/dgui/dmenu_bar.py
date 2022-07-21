from deposit_gui.dgui.dtool_bar import DToolBar

from PySide2 import (QtWidgets, QtCore, QtGui)

class DMenuBar(DToolBar):
	
	def __init__(self, view):
		
		DToolBar.__init__(self, view)
		
		self.menubar = self.view.menuBar()
		self.menubar.triggered.connect(self.on_triggered)
	
	def populate(self, tools):
		# tools = {menu: [(name, caption), None, ...], ...}; if None: add separator
		
		for menu_name in tools:
			menu = self.menubar.addMenu(menu_name)
			for name in tools[menu_name]:
				if name is None:
					menu.addSeparator()
				else:
					name, caption = name
					self.actions[name] = QtWidgets.QAction(caption, self.view)
					self.actions[name].setData(name)
					menu.addAction(self.actions[name])
