from PySide6 import (QtCore, QtWidgets, QtGui)

class ClassList(QtWidgets.QTreeWidget):
	
	def __init__(self, vnavigator):
		
		QtWidgets.QTreeWidget.__init__(self, vnavigator)
		
		self._vnavigator = vnavigator
		
		self._saved_selection = None
		
		self.setHeaderHidden(True)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		self.setExpandsOnDoubleClick(False)
		self.setIconSize(QtCore.QSize(24,24))
		self.setColumnCount(1)
		
		self.itemActivated.connect(self.on_activated)
		self.itemSelectionChanged.connect(self.on_selected)
	
	def populate(self, classes):
		
		selected = [(index.row(), index.parent().row()) for index in self.selectedIndexes()]
		
		self.clear()
		icon_obj = self._vnavigator.get_icon("object.svg")
		icon_cls = self._vnavigator.get_icon("class.svg")
		icon_descr = self._vnavigator.get_icon("descriptor.svg")
		
		items = []
		item = QtWidgets.QTreeWidgetItem()
		item.is_descriptor = False
		item.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, "[classless objects]")
		item.setData(0, QtCore.Qt.ItemDataRole.UserRole, "!*")
		item.setData(0, QtCore.Qt.ItemDataRole.DecorationRole, icon_obj)
		items.append(item)
		for cls in classes:
			item = QtWidgets.QTreeWidgetItem()
			item.is_descriptor = False
			item.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, cls.name)
			item.setData(0, QtCore.Qt.ItemDataRole.UserRole, cls)
			item.setData(0, QtCore.Qt.ItemDataRole.DecorationRole, icon_cls)
			subitems = []
			for descr in cls.get_descriptors(ordered = True):
				subitem = QtWidgets.QTreeWidgetItem()
				subitem.is_descriptor = True
				subitem.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, descr.name)
				subitem.setData(0, QtCore.Qt.ItemDataRole.UserRole, descr)
				subitem.setData(0, QtCore.Qt.ItemDataRole.DecorationRole, icon_descr)
				subitems.append(subitem)
			for cls_sub in cls.get_subclasses(ordered = True):
				subitem = QtWidgets.QTreeWidgetItem()
				subitem.is_descriptor = False
				subitem.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, cls_sub.name)
				subitem.setData(0, QtCore.Qt.ItemDataRole.UserRole, cls_sub)
				subitem.setData(0, QtCore.Qt.ItemDataRole.DecorationRole, icon_cls)
				subitems.append(subitem)
			if subitems:
				item.insertChildren(0, subitems)
			items.append(item)
		if items:
			self.insertTopLevelItems(0, items)	
		self.expandAll()
		if selected:
			if len(selected) > 1:
				self.blockSignals(True)
				for row, parent in selected[:-1]:
					parent = self.model().index(parent, 0)
					index = self.model().index(row, 0, parent)
					self.selectionModel().select(index, QtCore.QItemSelectionModel.SelectionFlag.Select)
				self.blockSignals(False)
			row, parent = selected[-1]
			parent = self.model().index(parent, 0)
			index = self.model().index(row, 0, parent)
			self.selectionModel().select(index, QtCore.QItemSelectionModel.SelectionFlag.Select)
			self.scrollTo(index)
			
	
	def get_selected(self):
		
		return [item.data(0, QtCore.Qt.ItemDataRole.UserRole) for item in self.selectedItems()]
	
	def get_selected_is_descriptor(self):
		
		selected = self.selectedItems()
		if not selected:
			return False
		return selected[0].is_descriptor
	
	def get_selected_parent(self):
		
		selected = self.selectedItems()
		if not selected:
			return None
		parent = selected[0].parent()
		if parent is None:
			return None
		return parent.data(0, QtCore.Qt.ItemDataRole.UserRole)
	
	def get_items_around_selected(self):
		
		indexes = self.selectedIndexes()
		if not indexes:
			return None, None
		
		above = self.indexAbove(indexes[0]).data(QtCore.Qt.ItemDataRole.UserRole)
		below = self.indexBelow(indexes[0]).data(QtCore.Qt.ItemDataRole.UserRole)
		
		return above, below
	
	def select_one_above(self):
		
		indexes = self.selectedIndexes()
		if not indexes:
			return
		index = self.indexAbove(indexes[0])
		self.selectionModel().select(index, QtCore.QItemSelectionModel.SelectionFlag.Select)
		self.setCurrentIndex(index)
	
	def select_one_below(self):
		
		indexes = self.selectedIndexes()
		if not indexes:
			return
		index = self.indexBelow(indexes[0])
		self.selectionModel().select(index, QtCore.QItemSelectionModel.SelectionFlag.Select)
		self.setCurrentIndex(index)
	
	def set_selected(self, names):
		
		iterator = QtWidgets.QTreeWidgetItemIterator(self)
		while iterator.value():
			item = iterator.value()
			name = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
			if name in names:
				item.setSelected(True)
				names.remove(name) # select only the first occurence of name
			iterator += 1
	
	@QtCore.Slot()
	def on_selected(self):
		
		self._vnavigator.on_class_selected(self.get_selected())
	
	@QtCore.Slot(object, int)
	def on_activated(self, item, column):

		cls = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
		parent = item.parent()
		if parent is not None:
			parent = parent.data(0, QtCore.Qt.ItemDataRole.UserRole)
		self._vnavigator.on_class_activated(cls, item.is_descriptor, parent)
	
	def focusInEvent(self, event):
		
		self._vnavigator.on_widget_activated()
		
		return QtWidgets.QTreeWidget.focusInEvent(self, event)
	
