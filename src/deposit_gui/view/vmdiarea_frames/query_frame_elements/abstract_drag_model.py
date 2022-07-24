from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_item import QueryItem

from PySide2 import (QtWidgets, QtCore)
import json

class AbstractDragModel(object):
	
	def __init__(self):
		
		self._queryframe = None
		self._proxy_model = None
		self._icons = None
	
	def supportedDragActions(self):
		
		return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction | QtCore.Qt.LinkAction | QtCore.Qt.ActionMask | QtCore.Qt.IgnoreAction
	
	def supportedDropActions(self):
		
		return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction | QtCore.Qt.LinkAction | QtCore.Qt.ActionMask | QtCore.Qt.IgnoreAction
	
	def flags(self, item):
		
		flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
		
		if item is None:
			return flags
		
		if self.drag_supported(item):
			flags = flags | QtCore.Qt.ItemIsDragEnabled
		
		if self.drop_supported(item):
			flags = flags | QtCore.Qt.ItemIsDropEnabled
		
		if not item.read_only:
			flags = flags | QtCore.Qt.ItemIsEditable
		
		return flags
	
	def mimeTypes(self):
		
		return ["application/deposit", "text/uri-list", "text/plain"]
	
	def mimeData(self, indexes):
		
		paths = []
		items = []
		datasource = self._queryframe._cmodel.get_datasource().to_dict()
		datasource["_id"] = id(self._queryframe._cmodel)
		for index in indexes:
			item = index.data(QtCore.Qt.UserRole)
			if item.is_resource():
				path = self._queryframe._cmodel.get_temp_copy(item.value)
				if path is not None:
					paths.append(path)
			item.datasource = datasource.copy()
			items.append(item.to_dict())
		
		data = QtCore.QMimeData()
		if items:
			items = bytes(json.dumps(items), "utf-8")
			data.setData("application/deposit", items)
			data_cb = QtCore.QMimeData() # workaround if deposit data gets reset while dragging
			data_cb.setData("application/deposit", items)
			cb = QtWidgets.QApplication.clipboard()
			cb.setMimeData(data_cb)
		if paths:
			data.setUrls([QtCore.QUrl().fromLocalFile(path) for path in paths])
		
		return data
	
	def process_drop(self, item, data):
		
		if "application/deposit" in data.formats():
			data = json.loads(data.data("application/deposit").data().decode("utf-8"))
			items = []
			for item_data in data:
				items.append(QueryItem(None).from_dict(item_data))
			if items:
				self.on_drop_items(item, items)
				return False
		
		if data.hasUrls():
			urls = [str(url.toString()) for url in data.urls()]
			if urls:	
				self.on_drop_url(item, urls)
				return False
		
		if data.hasText():
			self.on_drop_text(item, data.text())
			return False
		
		return False
	
	def dropMimeData(self, data, action, row, column, parent):
		
		item = parent.data(QtCore.Qt.UserRole)
		if item is None:
			return False
		return self.process_drop(item, data)
	
	def drag_supported(self, item):
		# re-implement to evaluate whether item supports drag
		# item: QueryItem
		
		return True
	
	def drop_supported(self, item):
		# re-implement to evaluate whether item supports drop
		# item: QueryItem
		
		return True
	
	def on_drop_url(self, item, urls):
		# re-implement to process drop of an url
		# item: QueryItem
		
		pass
		
	def on_drop_text(self, item, text):
		# re-implement to process drop of a text
		# item: QueryItem
		
		pass
		
	def on_drop_items(self, tgt_item, items):
		# re-implement to process drop of a list of QueryItems
		# tgt_item: QueryItem
		# items: [QueryItem, ...]
		
		pass
	
