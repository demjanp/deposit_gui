from deposit_gui.view.vmdiarea_frames.query_frame_elements.abstract_query_tab import AbstractQueryTab
from deposit_gui.view.vmdiarea_frames.query_frame_elements.abstract_drag_model import AbstractDragModel
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_item import QueryItem

from PySide2 import (QtWidgets, QtCore, QtGui)

class ImageDelegate(QtWidgets.QStyledItemDelegate):
	
	def __init__(self, query_tab_images):
		
		QtWidgets.QStyledItemDelegate.__init__(self, query_tab_images)
		
		self._query_tab_images = query_tab_images
	
	def paint(self, painter, option, index):
		
		self._query_tab_images._list_model.on_paint(index.data(QtCore.Qt.UserRole))
		
		QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)

class ProxyModel(QtCore.QSortFilterProxyModel):
	
	def __init__(self):
		
		super(ProxyModel, self).__init__()
		
		self._item_order = None
	
	def lessThan(self, source_left, source_right):
		
		def get_order(source):
			
			if self._item_order is None:
				return 0
			item = source.data(QtCore.Qt.UserRole)
			if item is None:
				return 0
			if item._key in self._item_order:
				return self._item_order[item._key]
			return 0
		
		return get_order(source_left) < get_order(source_right)
	
	def filterAcceptsRow(self, row, parent):
		
		if self._item_order is None:
			return True
		item = self.sourceModel().index(row, 0, parent).data(QtCore.Qt.UserRole)
		if item is None:
			return False
		if item._key in self._item_order:
			return True
		return False
	
	def sort(self, item_order):
		
		self._item_order = item_order
		
		QtCore.QSortFilterProxyModel.sort(self, 0, QtCore.Qt.DescendingOrder)
		QtCore.QSortFilterProxyModel.sort(self, 0, QtCore.Qt.AscendingOrder)
	
	def filter(self, item_order):
		
		self._item_order = item_order
		
		self.invalidateFilter()

class ListModel(AbstractDragModel, QtCore.QAbstractListModel):
	
	icon_loaded = QtCore.Signal(QtCore.QModelIndex)
	
	def __init__(self, queryframe, images, item_order, cmodel, icon_size = 256):
		
		QtCore.QAbstractListModel.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		self._cmodel = cmodel
		self._icon_size = icon_size
		self._proxy_model = ProxyModel()
		
		pixmap = QtGui.QPixmap(self._icon_size, self._icon_size)
		pixmap.fill()
		self.empty_icon = QtGui.QIcon(pixmap)
		
		self._proxy_model.setSourceModel(self)
		
		self.populate_data(images, item_order)
	
	def populate_data(self, images, item_order):
		
		self._icons = {} # {(row, col): QIcon or None, ...}; for each image
		self._images = images # {(row, col): DResource, ...}
		self._keys = sorted(list(images.keys()))
		self._item_order = item_order  # {(row, col): order, ...}
		
		self._proxy_model.sort(self._item_order)
	
	def rowCount(self, parent):
		
		return len(self._keys)
	
	def flags(self, index):
		
		item = self.data(index, QtCore.Qt.UserRole)
		
		return AbstractDragModel.flags(self, item)
	
	def data(self, index, role):
		
		key = self._keys[index.row()]
		
		if role == QtCore.Qt.DisplayRole:
			return self._images[key].filename
		
		if role == QtCore.Qt.DecorationRole:
			icon = self._icons.get(key, None)
			if icon is None:
				return self.empty_icon
			return icon
		
		if role == QtCore.Qt.UserRole:
			class_name, descriptor_name = self._query.columns[key[1]]
			value = self._images[key]
			obj_id = list(value.object_ids)
			obj_id = obj_id[0] if obj_id else None
			item = QueryItem(index, class_name, descriptor_name, obj_id, value)
			item._key = key
			
			return item
		
		return None
	
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
		
		return
		
	def on_drop_items(self, tgt_item, items):
		# tgt_item: QueryItem
		# items: [QueryItem, ...]
		
		if items:
			self._queryframe.on_edited(tgt_item, items[0].value)
	
	def on_paint(self, item):
		
		if item is None:
			return
		
		key = item._key
		if self._icons.get(key, None) is None:
			path = self._cmodel.get_thumbnail(item.value, self._icon_size)
			if path is not None:
				self._icons[key] = QtGui.QIcon(path)
				self.icon_loaded.emit(self._proxy_model.mapFromSource(item.index))
		
	def on_close(self):
		
		pass

class ListView(AbstractQueryTab, QtWidgets.QListView):
	
	def __init__(self, queryframe, header, images, item_order, cmodel, icon_size = 256):
		
		QtWidgets.QListView.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		self._header = header
		self._icon_size = icon_size
		self._thumbnail_size = icon_size
		
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
		self.setDefaultDropAction(QtCore.Qt.CopyAction)
		self.setDropIndicatorShown(True)
		
		self.setItemDelegate(ImageDelegate(self))
		self._list_model = ListModel(queryframe, images, item_order, cmodel, self._icon_size)
		
		self.setViewMode(QtWidgets.QListView.IconMode)
		self.setUniformItemSizes(True)
		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.setResizeMode(QtWidgets.QListView.Adjust)
		self.setWrapping(True)
		self.setFlow(QtWidgets.QListView.LeftToRight)
		
		self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
		
		self.setModel(self._list_model._proxy_model)
		
		self._list_model.icon_loaded.connect(self.update)
		
		self.activated.connect(self.on_activated)
	
	def update_query(self, images, item_order):
		
		self._list_model.beginResetModel()
		self._list_model.populate_data(images, item_order)
		self._list_model.endResetModel()
	
	def get_row_count(self):
		
		return self._list_model._proxy_model.rowCount()
	
	def set_thumbnail_size(self, value):
		
		self._thumbnail_size = value
		self.setIconSize(QtCore.QSize(value, value))
	
	def sort(self, item_order):
		
		self._list_model._proxy_model.sort(item_order)
	
	def apply_filter(self, item_order):
		
		self._list_model._proxy_model.filter(item_order)
	
	@QtCore.Slot(QtCore.QModelIndex)
	def on_activated(self, index):
		
		item = index.data(QtCore.Qt.UserRole)
		self._queryframe.on_query_activated(item)
	
	def on_selected(self):
		
		items = [index.data(QtCore.Qt.UserRole) for index in self.selectionModel().selectedIndexes()]
		items = [item for item in items if item is not None]
		self._queryframe.on_query_selected(items)
		self._header.set_to_object_enabled(len(items) == 1)
		if items:
			self._header.set_object(items[0].obj_id)
		else:
			self._header.set_object(None)
	
	def on_close(self):
		
		self._list_model.on_close()
	
	def selectionChanged(self, *args, **kwargs):
		
		QtWidgets.QListView.selectionChanged(self, *args, **kwargs)
		
		self.on_selected()

class ListHeader(QtWidgets.QFrame):
	
	def __init__(self, queryframe):
		
		QtWidgets.QFrame.__init__(self)
		
		self._queryframe = queryframe
		self._obj_id = None
		
		self.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.setFrameShadow(QtWidgets.QFrame.Raised)
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(5, 0, 0, 0)
		self.layout().setSpacing(0)
		
		self.to_object_button = QtWidgets.QToolButton()
		self.to_object_button.setIcon(self._queryframe.get_icon("to_object.svg"))
		self.to_object_button.setIconSize(QtCore.QSize(24, 24))
		self.to_object_button.setAutoRaise(True)
		self.to_object_button.setToolTip("Select Object")
		self.to_object_button.setContentsMargins(0, 0, 10, 0)
		self.to_object_button.setEnabled(False)
		self.to_object_button.clicked.connect(lambda state: self._queryframe.on_to_object(self._obj_id))
		self.layout().addWidget(self.to_object_button)
		
		zoom_label = QtWidgets.QLabel("Zoom:")
		zoom_label.setContentsMargins(5, 0, 5, 0)
		self.layout().addWidget(zoom_label)
		self.zoom_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
		self.zoom_slider.setMinimum(64)
		self.zoom_slider.setMaximum(256)
		self.zoom_slider.setMaximumWidth(400)
		self.zoom_slider.valueChanged.connect(self._queryframe.on_zoom)
		self.layout().addWidget(self.zoom_slider)
		
		self.layout().addStretch()
	
	def set_object(self, obj_id):
		
		self._obj_id = obj_id
	
	def set_to_object_enabled(self, state):
		
		self.to_object_button.setEnabled(state)
	
	def set_zoom_slider(self, value):

		self.blockSignals(True)
		self.zoom_slider.setValue(value)
		self.blockSignals(False)


class QueryTabImagesLazy(AbstractQueryTab, QtWidgets.QWidget):
	
	def __init__(self, queryframe):
		
		QtWidgets.QWidget.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		self._has_image = None
		
	def has_image(self):
		
		if self._has_image is None:
			for row in self._query:
				for _, value in row:
					if (value.__class__.__name__ == "DResource") and value.is_image:
						self._has_image = True
						return True
			self._has_image = False
		return self._has_image
	
	def get_row_count(self):
		
		return int(self.has_image())
	
	def set_thumbnail_size(self, value):
		
		pass
	
	def sort(self, item_order):
		
		pass
	
	def clearSelection(self):
		
		pass

class QueryTabImages(AbstractQueryTab, QtWidgets.QFrame):
	
	def __init__(self, queryframe, images, item_order, cmodel, icon_size = 256):
		
		QtWidgets.QFrame.__init__(self)
		
		self._list_header = ListHeader(queryframe)
		self._list_view = ListView(queryframe, self._list_header, images, item_order, cmodel, icon_size)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().addWidget(self._list_header)
		self.layout().addWidget(self._list_view)
	
	def set_thumbnail_size(self, value):
		
		self._list_header.set_zoom_slider(value)
		self._list_view.set_thumbnail_size(value)
	
	def update_query(self, images, item_order):
		
		self._list_view.update_query(images, item_order)
	
	def get_row_count(self):
		
		return self._list_view.get_row_count()
	
	def apply_filter(self, item_order):
		
		self._list_view.apply_filter(item_order)
	
	def sort(self, item_order):
		
		self._list_view.sort(item_order)
	
	def clearSelection(self):
		
		self._list_view.clearSelection()
	
	def on_selected(self):
		
		self._list_view.on_selected()
	
	def on_close(self):
		
		self._list_view.on_close()

