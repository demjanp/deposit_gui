from deposit_gui.dgui.dtool_bar import DToolBar

from PySide2 import (QtWidgets, QtCore, QtGui)

class DMenuBar(DToolBar):
	
	def __init__(self, view):
		
		DToolBar.__init__(self, view)
		
		self.menubar = self.view.menuBar()
		self.menubar.triggered.connect(self.on_triggered)
		
		self.menus = {}  # {name: QMenu, ...}
	
	def set_menu_enabled(self, name, state):
		
		if name not in self.menus:
			return
		self.menus[name].setEnabled(state)
	
	def populate(self, tools):
		# tools = {menu: [(name, caption), None, ...], ...}; if None: add separator
		
		def populate_menu(items, menu):
			
			for name in items:
				if name is None:
					menu.addSeparator()
				elif isinstance(name[1], str):
					name, caption = name
					self.actions[name].append(QtWidgets.QAction(caption, self.view))
					self.actions[name][-1].setData(name)
					menu.addAction(self.actions[name][-1])
				elif isinstance(name[1], list):
					submenu = QtWidgets.QMenu(name[0])
					menu.addMenu(submenu)
					populate_menu(name[1], submenu)
		
		for menu_name in tools:
			self.menus[menu_name] = self.menubar.addMenu(menu_name)
			populate_menu(tools[menu_name], self.menus[menu_name])
