from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.view.vmdiarea import VMDIArea
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_item import QueryItem
from deposit.store.abstract_delement import AbstractDElement
from deposit.utils.fnc_serialize import (try_numeric)
from deposit.utils.fnc_files import (url_to_path)
from deposit import DResource
from deposit import externalsource as Externalsource
from deposit import Store

from PySide2 import (QtCore)
import json
import os

class CMDIArea(AbstractSubcontroller):
	
	def __init__(self, cmain) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vmdiarea = VMDIArea(self.on_drag_enter, self.on_drag_move, self.on_drop)
		
		self._vmdiarea.signal_window_activated.connect(self.cmain.on_mdiarea_activated)
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	@QtCore.Slot(object)
	def on_query_add_object(self, query):
		
		cls = query.main_class
		if cls == "*":
			return
		if cls is None:
			self.cmain.cmodel.add_object()
		else:
			cls = self.cmain.cmodel.get_class(cls)
			if cls:
				cls.add_member()
	
	@QtCore.Slot()
	def on_query_del_object(self):
		
		objects = self.cmain.get_selected_objects()
		if objects:
			self.cmain.cdialogs.open("DelObjects", objects)
	
	@QtCore.Slot()
	def on_query_del_descriptor(self):
		
		for item in self.cmain.get_selected_queryitems():
			if (item.obj_id is None) or (item.class_name is None) or (item.descriptor_name is None):
				continue
			obj = self.cmain.cmodel.get_object(item.obj_id)
			obj.del_descriptor(item.descriptor_name)
	
	@QtCore.Slot(object)
	def on_query_activated(self, item):
		
		if isinstance(item.value, DResource):
			url = self.cmain.cmodel.get_updated_url(item.value)
			self.cmain.open_in_external(url_to_path(url))
	
	@QtCore.Slot(object, object)
	def on_query_edited(self, item, value):
		
		descr = self.cmain.cmodel.get_class(item.descriptor_name)
		obj = self.cmain.cmodel.get_object(item.obj_id)
		if (descr is None) or (obj is None):
			return
		# TODO try json.dumps(value) for dicts and lists
		# TODO detect datetime in ISO format
		if not isinstance(value, AbstractDElement):
			value = try_numeric(value)
			if value == "":
				value = None
		obj.set_descriptor(descr, value)
	
	@QtCore.Slot(object, str)
	def on_query_drop_url(self, item, url):
		
		descr = self.cmain.cmodel.get_class(item.descriptor_name)
		obj = self.cmain.cmodel.get_object(item.obj_id)
		if (descr is None) or (obj is None):
			return
		obj.set_resource_descriptor(descr, url)
	
	@QtCore.Slot(object)
	def on_class_activated(self, cls):
		
		self.add_query("SELECT [%s].*" % (cls.name))
	
	@QtCore.Slot(str)
	def on_class_link(self, name):
		
		self.add_query("SELECT [%s].*" % (name))
	
	@QtCore.Slot(int, str, str)
	def on_relation_link(self, obj_id, label, name_tgt):
		
		self.add_query("SELECT [%s].*, OBJ(%d).* RELATED OBJ(%d).[%s].[%s]" % (name_tgt, obj_id, obj_id, label, name_tgt))
	
	@QtCore.Slot(int, str, str)
	def on_relation_unlink(self, obj_id, label, name_tgt):
		
		obj = self.cmain.cmodel.get_object(obj_id)
		to_del = []
		for obj_tgt, label_ in obj.get_relations():
			if (label_ == label) and obj_tgt.has_class(name_tgt):
				to_del.append(obj_tgt)
		for obj_tgt in to_del:
			obj.del_relation(obj_tgt, label)
	
	def get_drag_data(self, event):
		# returns type, data; type = "query_items" / "url" / None
		
		mimedata = event.mimeData()
		if "application/deposit" in mimedata.formats():
			rows = mimedata.data("application/deposit")
			rows = rows.data().decode("utf-8").strip()
			if not rows:
				cb = QtWidgets.QApplication.clipboard()
				mimedata = cb.mimeData()
				if "application/deposit" in mimedata.formats():
					rows = mimedata.data("application/deposit")
					rows = rows.data().decode("utf-8").strip()
			if rows:
				items = []
				rows = json.loads(rows)
				for row in rows:
					items.append(QueryItem(None).from_dict(row))
				return "query_items", items
		
		if mimedata.hasUrls():
			for url in mimedata.urls():
				url = str(url.toString())
				if url.split(".")[-1].lower() in ["json", "pickle", "xlsx", "csv", "shp"]:
					return "url", url
		
		return None, None
	
	def on_drag_enter(self, event):
		
		typ, data = self.get_drag_data(event)
		if typ is None:
			event.ignore()
			return
		event.accept()
	
	def on_drag_move(self, event):
		
		typ, data = self.get_drag_data(event)
		if typ is None:
			event.ignore()
			return
		event.accept()
	
	def on_drop(self, event):
		
		typ, data = self.get_drag_data(event)
		if typ == "url":
			url = "%s" % (data)
			ext = url.split(".")[-1].lower()
			if ext in ["json", "pickle"]:
				self.cmain.cdialogs.open("ConfirmLoad", url)
				return
			self.add_external(url)
			return
		
		if typ == "query_items":
			items = []
			datasource = None
			for item in data:
				if item.datasource.get("_id", None) == id(self.cmain.cmodel):
					return
				if item.datasource.get("datasource", "Memory") == "Memory":
					continue
				datasource = item.datasource
				items.append(item)
			if datasource is None:
				self.cmain.cview.show_warning("Import Error", "Cannot import from an unsaved database.")
			else:
				self.cmain.cview.progress.show("Loading")
				store = Store(keep_temp = True)
				store.load(progress = self.cmain.cview.progress, **datasource)
				self.cmain.cview.progress.stop()
				objects = []
				for item in items:
					objects.append(store.get_object(item.obj_id_row))
				sub_store = store.get_subgraph(objects)
				if not store.get_objects():
					return
				self.cmain.cdialogs.open("ImportStore", sub_store)
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	def get_current_frame(self):
		
		return self._vmdiarea.get_current_frame()
	
	def update_queries(self, objects, classes):
		
		for query_frame in self._vmdiarea.get_query_frames():
			query_frame.update_query(objects, classes)
	
	def update_class_graphs(self):
		
		for class_graph_frame in self._vmdiarea.get_class_graph_frames():
			class_graph_frame.update_classes()
	
	def set_background_text(self, text):
		
		self._vmdiarea.set_background_text(text)
	
	def add_query(self, querystr):
		
		query = self.cmain.cmodel.get_query(querystr)
		query_frame = self._vmdiarea.add_query_frame(query, self.cmain.cmodel, self.cmain.cview)
		query_frame.signal_query_selected.connect(self.cmain.on_query_selected)
		query_frame.signal_query_activated.connect(self.on_query_activated)
		query_frame.signal_object_selected.connect(self.cmain.on_object_selected)
		query_frame.signal_relation_selected.connect(self.cmain.on_relation_selected)
		query_frame.signal_class_link.connect(self.on_class_link)
		query_frame.signal_relation_link.connect(self.on_relation_link)
		query_frame.signal_relation_unlink.connect(self.on_relation_unlink)
		query_frame.signal_add_object.connect(self.on_query_add_object)
		query_frame.signal_del_object.connect(self.on_query_del_object)
		query_frame.signal_del_descriptor.connect(self.on_query_del_descriptor)
		query_frame.signal_edited.connect(self.on_query_edited)
		query_frame.signal_drop_url.connect(self.on_query_drop_url)
		self.cmain.cquerytoolbar.set_query_text(querystr)
	
	def add_class_graph(self):
		
		class_graph_frame = self._vmdiarea.add_class_graph_frame(self.cmain.cmodel, self.cmain.cview)
		class_graph_frame.signal_class_selected.connect(self.cmain.on_class_selected)
		class_graph_frame.signal_relation_selected.connect(self.cmain.on_relation_selected)
		class_graph_frame.signal_activated.connect(self.on_class_activated)
	
	def add_external(self, url):
		
		source = os.path.splitext(url)[-1].strip(".").upper()
		if not hasattr(Externalsource, source):
			return
		self._vmdiarea.add_external_frame(source, url = url)
	
	def deselect_all(self):
		
		self._vmdiarea.deselect_all()
	
	def close_all(self):
		
		self._vmdiarea.close_all()

