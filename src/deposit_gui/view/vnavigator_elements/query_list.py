from PySide6 import (QtCore, QtWidgets, QtGui)

class QueryList(QtWidgets.QListWidget):
	
	def __init__(self, vnavigator):
		
		QtWidgets.QListWidget.__init__(self, vnavigator)
		
		self._vnavigator = vnavigator
		
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		
		self.itemActivated.connect(self.on_activated)
		self.itemSelectionChanged.connect(self.on_selected)
		
	def populate(self, queries):
		
		selected = self.get_selected()
		
		self.clear()
		
		for title in queries:
			self.addItem(QtWidgets.QListWidgetItem(title))
		
		if selected:
			for row in range(self.count()):
				item = self.item(row)
				if item.text() in selected:
					item.setSelected(True)
	
	def get_selected(self):
		
		return [item.text() for item in self.selectedItems()]
	
	@QtCore.Slot(object)
	def on_activated(self, item):
		
		self._vnavigator.on_query_activated(item.text())
	
	@QtCore.Slot()
	def on_selected(self):
		
		self._vnavigator.on_query_selected(self.get_selected())
	
	def focusInEvent(self, event):
		
		self._vnavigator.on_widget_activated()
		
		return QtWidgets.QTreeWidget.focusInEvent(self, event)
	
