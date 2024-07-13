from deposit_gui.view.vmdiarea_frames.query_frame_elements.abstract_query_tab import AbstractQueryTab
from deposit_gui.view.vmdiarea_frames.query_frame_elements.abstract_drag_model import AbstractDragModel
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_item import QueryItem

import deposit_gui
import os

from PySide6 import (QtWidgets, QtCore, QtGui)
from natsort import (natsorted)

class ProxyModel(QtCore.QSortFilterProxyModel):
	
	signal_sorted = QtCore.Signal()
	
	def __init__(self):
		
		super(ProxyModel, self).__init__()
	
	def lessThan(self, source_left, source_right):
		
		values = [("" if val is None else val) for val in [source_left.data(QtCore.Qt.ItemDataRole.DisplayRole), source_right.data(QtCore.Qt.ItemDataRole.DisplayRole)]]
		
		return values == natsorted(values)
	
	def sort(self, *args):
		
		QtCore.QSortFilterProxyModel.sort(self, *args)
		
		self.signal_sorted.emit()

class TableModel(AbstractDragModel, QtCore.QAbstractTableModel):
	
	def __init__(self, queryframe):
		
		QtCore.QAbstractTableModel.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		self._proxy_model = ProxyModel()
		self._icons = dict(
			obj = self._queryframe.get_icon("object.svg"),
			geo = self._queryframe.get_icon("geometry.svg"),
			file = self._queryframe.get_icon("file.svg"),
			image = self._queryframe.get_icon("image.svg"),
			remote_file = self._queryframe.get_icon("remote_file.svg"),
			remote_image = self._queryframe.get_icon("remote_image.svg"),
		)
		self.populate_data()
		
		self._proxy_model.setSourceModel(self)
		self._proxy_model.signal_sorted.connect(self._queryframe.on_sorted)
	
	def populate_data(self):
		
		self._query_items = {}
		self._ro_columns = [True] * len(self._query.columns)
		if self._query.main_class not in [None, "*"]:
			self._ro_columns = [(class_name != self._query.main_class) for class_name, _ in self._query.columns]
		
		self._column_names = []
		for class_name, descriptor_name in self._query.columns:
			names = [name for name in [class_name, descriptor_name] if isinstance(name, str)]
			if names:
				self._column_names.append(".".join(names))
			else:
				self._column_names.append("[no class]")
	
	def get_query_item(self, index):
		
		if not index.isValid():
			return QueryItem(index)
		
		row, col = index.row(), index.column()
		
		key = (row, col)
		if key not in self._query_items:
			obj_id, value = self._query[row, col]
			obj_id_row, _ = self._query[row, 0]
			class_name, descriptor_name = self._query.columns[col]
			self._query_items[key] = QueryItem(index, class_name, descriptor_name, obj_id, value, self._icons, self._ro_columns[col], obj_id_row = obj_id_row)
		
		return self._query_items[key]
	
	def rowCount(self, parent):
		
		return len(self._query)
	
	def columnCount(self, parent):

		return len(self._query.columns)
	
	def flags(self, index):
		
		item = self.get_query_item(index)
		
		return AbstractDragModel.flags(self, item)
	
	def headerData(self, section, orientation, role):
		
		if orientation == QtCore.Qt.Orientation.Horizontal: # column headers
			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return self._column_names[section]
			elif role == QtCore.Qt.ItemDataRole.UserRole:
				return self._query.columns[section]
			return None
		
		if orientation == QtCore.Qt.Orientation.Vertical: # row headers
			index = self._proxy_model.index(section, 0)
			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return str(self.get_query_item(index).obj_id_row)
			elif role == QtCore.Qt.ItemDataRole.UserRole:
				return self.get_query_item(index).obj_id_row
			
		return None
	
	def data(self, index, role):
		
		if not index.isValid():
			return None
		
		item = self.get_query_item(index)
		
		return item.data(role)
	
	def setData(self, index, value, role = QtCore.Qt.ItemDataRole.EditRole):
		
		if role == QtCore.Qt.ItemDataRole.EditRole:
			item = self.get_query_item(index)
			QtCore.QAbstractTableModel.setData(self, index, value, role)
			self._queryframe.on_edited(item, value)
		
		return False
	
	def drag_supported(self, item):
		# item: QueryItem
		
		return True
	
	def drop_supported(self, item):
		# item: QueryItem
		
		return True
	
	def on_drop_url(self, item, urls):
		# item: QueryItem
		
		if urls:
			self._queryframe.on_drop_url(item, urls[0])
		
	def on_drop_text(self, item, text):
		# item: QueryItem
		
		self.setData(item.index, text)
		
	def on_drop_items(self, tgt_item, items):
		# tgt_item: QueryItem
		# items: [QueryItem, ...]
		
		if items:
			self._queryframe.on_edited(tgt_item, items[0].value)

class QueryTabTable(AbstractQueryTab, QtWidgets.QTableView):
	
	def __init__(self, queryframe):
		
		QtWidgets.QTableView.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		self._table_model = TableModel(queryframe)
		
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
		self.setDefaultDropAction(QtCore.Qt.DropAction.CopyAction)
		self.setDropIndicatorShown(True)
		
		self.setSortingEnabled(True)
		self.horizontalHeader().setSortIndicator(0, QtCore.Qt.SortOrder.AscendingOrder)
		
		path = os.path.join(os.path.dirname(deposit_gui.__file__), "res/obj_id.svg")
		path = path.replace("\\", "/")
		self.setStyleSheet('''
			QTableView::item:selected:!active {
				background-color : #81b0d6;
			}
			QTableCornerButton::section {
				background-color: #FFFFFF;
				background-image: url(\"%s\");
				background-position: center;
				background-repeat: no-repeat;
				border: 0px solid lightgrey;
				border-width: 0 1px 0 0;
			}
			QHeaderView::section:vertical {
				width: 50px;
			}
			QHeaderView::section:horizontal {
				height: 30px;
			}
		''' % (path))
		
		self.setIconSize(QtCore.QSize(24, 24))
		
		self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		self.horizontalHeader().setStretchLastSection(True)
		
		self.setModel(self._table_model._proxy_model)
		
		self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		
		self.activated.connect(self.on_activated)
		self.verticalHeader().sectionDoubleClicked.connect(self.on_row_doubleclicked)
	
	def update_query(self):
		
		self._table_model.beginResetModel()
		self._table_model.populate_data()
		self._table_model.endResetModel()
	
	def apply_filter(self, text):
		
		if text == "":
			self._table_model._proxy_model.setFilterWildcard("")
		else:
			self._table_model._proxy_model.setFilterRegularExpression(
				QtCore.QRegularExpression(".*%s.*" % text, QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption))
		self._table_model._proxy_model.setFilterKeyColumn(-1)
	
	def select_object(self, obj_id):
		
		for row in range(self._table_model._proxy_model.rowCount()):
			if self._table_model._proxy_model.index(row, 0).data(QtCore.Qt.ItemDataRole.UserRole).obj_id_row == obj_id:
				self.selectRow(row)
				return
	
	def get_item(self, row, col):
		
		index = self._table_model._proxy_model.index(row, col)
		return self._table_model._proxy_model.mapToSource(index).data(QtCore.Qt.ItemDataRole.UserRole)
	
	def set_query_item(self, row, column, value):
		
		self._table_model._proxy_model.setData(self._table_model._proxy_model.index(row, column), value)
	
	def get_row_count(self):
		
		return self._table_model._proxy_model.rowCount()
	
	def get_column_count(self):
		
		return self._table_model._proxy_model.columnCount()
	
	def get_images(self):
		
		images = {}
		n_columns = len(self._query.columns)
		for row in range(len(self._query)):
			for column in range(n_columns):
				value = self._table_model.index(row, column).data(QtCore.Qt.ItemDataRole.UserRole)
				if isinstance(value, QueryItem):
					value = value.value
					if (value.__class__.__name__ == "DResource") and (value.is_image):
						images[(row, column)] = value
		return images
	
	def get_obj_ids(self):
		# return objects of currently visible rows
		
		obj_ids = set()
		for row in range(self._table_model._proxy_model.rowCount()):
			index = self._table_model._proxy_model.index(row, 0)
			item = self._table_model._proxy_model.mapToSource(index).data(QtCore.Qt.ItemDataRole.UserRole)
			if isinstance(item, QueryItem):
				obj_id = item.obj_id
				if obj_id is not None:
					obj_ids.add(obj_id)
		return obj_ids
	
	def get_item_order(self):
		# return ordering of items according to current sorting
		#
		# returns item_order[(row, col)] = order
		
		item_order = {}
		n_columns = len(self._query.columns)
		for row in range(self._table_model._proxy_model.rowCount()):
			for column in range(n_columns):
				index = self._table_model._proxy_model.index(row, column)
				index_orig = self._table_model._proxy_model.mapToSource(index)
				item_order[(index_orig.row(), index_orig.column())] = index.row() * n_columns + index.column()
		return item_order
	
	@QtCore.Slot(QtCore.QModelIndex)
	def on_activated(self, index):
		
		item = index.data(QtCore.Qt.ItemDataRole.UserRole)
		self._queryframe.on_query_activated(item)
	
	@QtCore.Slot(int)
	def on_row_doubleclicked(self, row):
		
		self.on_activated(self._table_model._proxy_model.index(row, 0))
	
	def on_selected(self):
		
		row_items = [index.data(QtCore.Qt.ItemDataRole.UserRole) for index in self.selectionModel().selectedRows()]
		items = [index.data(QtCore.Qt.ItemDataRole.UserRole) for index in self.selectionModel().selectedIndexes()]
		items = [item for item in items if item is not None]
		self._queryframe.on_query_selected(items)
		self._queryframe.on_selected_rows(row_items)
	
	def selectionChanged(self, *args, **kwargs):
		
		QtWidgets.QTableView.selectionChanged(self, *args, **kwargs)
		
		self.on_selected()


