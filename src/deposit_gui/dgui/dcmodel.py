from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.dgui.dmodel import DModel

from deposit import (DDateTime, DGeometry, DResource)
from deposit.datasource import AbstractDatasource

from deposit.utils.fnc_files import (as_url)
from deposit.utils.fnc_serialize import (try_numeric, value_to_str)
from deposit.query.parse import (remove_bracketed_selects, extract_expr_vars)

from PySide2 import (QtCore)
from collections import defaultdict
from natsort import natsorted

class DCModel(AbstractSubcontroller):
	
	def __init__(self, cmain, store = None):
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._progress = None
		
		self._model = DModel(store)
		
		self._model.signal_store_event.connect(self.on_store_event)
		self._model.signal_store_error.connect(self.on_error)
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	@QtCore.Slot(int, list, list, object)
	def on_store_event(self, event, objects, classes, datasource):
		
		if event == DModel.EVENT_ADDED:
			self.on_added(objects, classes)
		elif event == DModel.EVENT_DELETED:
			self.on_deleted(objects, classes)
		elif event == DModel.EVENT_CHANGED:
			self.on_changed(objects, classes)
		elif event == DModel.EVENT_SAVED:
			self.on_saved(datasource)
		elif event == DModel.EVENT_LOADED:
			self.on_loaded()
		elif event == DModel.EVENT_LOCAL_FOLDER_CHANGED:
			self.on_local_folder_changed()
		elif event == DModel.EVENT_QUERIES_CHANGED:
			self.on_queries_changed()
		elif event == DModel.EVENT_USER_TOOLS_CHANGED:
			self.on_user_tools_changed()
		elif event == DModel.EVENT_SETTINGS_CHANGED:
			self.on_settings_changed()
	
	@QtCore.Slot(str)
	def on_error(self, message):
		
		pass
	
	def on_added(self, objects, classes):
		# elements = [DObject, DClass, ...]
		
		pass
	
	def on_deleted(self, objects, classes):
		# elements = [obj_id, name, ...]
		
		pass
	
	def on_changed(self, objects, classes):
		# elements = [DObject, DClass, ...]
		
		pass
	
	def on_saved(self, datasource):
		
		pass
	
	def on_loaded(self):
		
		pass
	
	def on_local_folder_changed(self):
		
		pass
	
	def on_queries_changed(self):
		
		pass
	
	def on_user_tools_changed(self):
		
		pass
	
	def on_settings_changed(self):
		
		pass
		
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	
	# ---- General
	# ------------------------------------------------------------------------
	def set_progress(self, progress):
		
		self._progress = progress
	
	def get_descriptor_names(self):
		
		return self._model.get_descriptor_names(ordered = True)
	
	def get_relation_labels(self):
		
		return self._model.get_relation_labels()
	
	def reverse_relation(self, label):
		
		if label.startswith("~"):
			return label[1:]
		return "~" + label
	
	def get_subgraph(self, objects):
		
		if self._progress is not None:
			self._progress.show("Extracting Subgraph")
		store = self._model.get_subgraph(
			objects, 
			progress = self._progress
		)
		if self._progress is not None:
			self._progress.stop()
		return store
	
	def get_thumbnail(self, resource, size = 256):
		
		return self._model.get_thumbnail(resource, size)
	
	def get_folder(self):
		
		return self._model.get_folder()
	
	def get_temp_folder(self, name):
		
		return self._model.get_temp_folder(name)
	
	def get_temp_copy(self, resource):
		
		return self._model.get_temp_copy(resource)
	
	def get_updated_url(self, resource):
		
		return self._model.get_updated_url(resource)
	
	def get_query(self, querystr, silent = False):
		
		if (not silent) and (self._progress is not None):
			self._progress.show("Processing Query")
		query = self._model.get_query(
			querystr, 
			progress = (None if silent else self._progress)
		)
		if (not silent) and (self._progress is not None):
			self._progress.stop()
		return query
	
	def has_local_folder(self):
		
		return self._model.has_local_folder()
	
	def set_local_folder(self, path):
		
		self._model.set_local_folder(path, progress = self._progress)
	
	def prune_resources(self):
		
		if self._progress is not None:
			self._progress.show("Pruning Resources")
		self._model.prune_resources()
		if self._progress is not None:
			self._progress.stop()
	
	def can_save(self):
		
		datasource = self._model.get_datasource()
		
		return datasource.__class__.__name__ != "Memory"
	
	def field_calculator(self, target, expr, rows):
		
		if (not target) or (not expr) or (not rows):
			return
		classes = set(self.get_class_names())
		descriptors = set(self.get_descriptor_names())
		expr, bracketed_selects = remove_bracketed_selects(
			expr, classes, descriptors
		)
		expr, vars = extract_expr_vars(
			expr.strip(), classes, descriptors, bracketed_selects
		)
		for obj_id in rows:
			obj = self.get_object(obj_id)
			values = dict(
				DDateTime = DDateTime,
				DGeometry = DGeometry,
				DResource = DResource,
			)
			for name in vars:
				values[name] = rows[obj_id].get(vars[name], None)
			value = eval(expr, values)
			if value is not None:
				obj.set_descriptor(target, value)
	
	def merge_objects(self, objects):
		# objects = [obj_id, ...]
		
		data = {}
		locations = {}
		relations = set()
		for obj_id in objects:
			obj = self.get_object(obj_id)
			for descr in obj.get_descriptors():
				if descr not in data:
					value = obj.get_descriptor(descr)
					if value is not None:
						data[descr] = value
						location = obj.get_location(descr)
						if location is not None:
							locations[descr] = location
		for obj_id in objects[1:]:
			obj = self.get_object(obj_id)
			for obj_tgt, label in obj.get_relations():
				weight = obj.get_relation_weight(obj_tgt, label)
				relations.add((obj_tgt, label, weight))
		obj = self.get_object(objects[0])
		for descr in data:
			obj.set_descriptor(descr, data[descr])
		for descr in locations:
			obj.set_location(descr, locations[descr])
		for obj_tgt, label, weight in relations:
			obj.add_relation(obj_tgt, label, weight)
		for obj_id in objects[1:]:
			self.del_object(obj_id)
	
	def merge_identical(self, objects):
		# objects = set(obj_id, ...)
		
		grouped = defaultdict(set)
		for obj_id in objects:
			obj = self.get_object(obj_id)
			key = [(descr.name, value_to_str(obj.get_descriptor(descr))) for \
				descr in obj.get_descriptors()]
			grouped[tuple(sorted(key, key = lambda item: item[0]))].add(obj)
		for key in grouped:
			if len(grouped[key]) > 1:
				obj = grouped[key].pop()
				relations = set()
				for obj2 in grouped[key]:
					for obj_tgt, label in obj.get_relations():
						weight = obj.get_relation_weight(obj_tgt, label)
						relations.add((obj_tgt, label, weight))
				for obj_tgt, label, weight in relations:
					obj.add_relation(obj_tgt, label, weight)
				for obj2 in grouped[key]:
					self.del_object(obj2)
	
	def duplicate(self, objects):
		# objects = set(obj_id, ...)
		
		for obj_id in objects:
			obj = self.get_object(obj_id)
			obj2 = self.add_object()
			for descr in obj.get_descriptors():
				obj2.set_descriptor(descr, obj.get_descriptor(descr))
				location = obj.get_location(descr)
				if location is not None:
					obj2.set_location(descr, location)
			for cls in obj.get_classes():
				cls.add_member(obj2)
	
	
	# ---- Object
	# ------------------------------------------------------------------------
	def add_object(self):
		
		return self._model.add_object()
	
	def get_object(self, obj_id):
		
		return self._model.get_object(obj_id)
	
	def del_object(self, obj_id):
		
		self._model.del_object(obj_id)
	
	def del_objects(self, obj_ids):
		
		self._model.blockSignals(True)
		if self._progress is not None:
			self._progress.show("Deleting")
			self._progress.update_state(value = 0, maximum = len(obj_ids))
		cnt = 1
		for obj_id in obj_ids:
			if self._progress is not None:
				if self._progress.cancel_pressed():
					break
			self._model.del_object(obj_id)
			if self._progress is not None:
				self._progress.update_state(value = cnt)
			cnt += 1
		self._model.blockSignals(False)
		self._model.on_deleted(obj_ids)
	
	
	# ---- Class
	# ------------------------------------------------------------------------
	def add_class(self, name):
		
		return self._model.add_class(name)
	
	def get_class(self, name):
		
		return self._model.get_class(name)
	
	def get_classes(self):
		
		return self._model.get_classes(ordered = True)
	
	def get_class_names(self, ordered = False):
		
		return self._model.get_class_names(ordered)
	
	def get_class_values(self, class_name, descriptor_name):
		
		values = set()
		cls = self._model.get_class(class_name)
		if cls is None:
			return []
		for obj in cls.get_members():
			val = obj.get_descriptor(descriptor_name)
			if val is not None:
				values.add(val)
		values = natsorted(values)
		
		return values
	
	def get_descriptor_names(self, ordered = False):
		
		return self._model.get_descriptor_names(ordered)
	
	def rename_class(self, cls, name):
		
		self._model.rename_class(cls, name)
	
	def rename_class_descriptor(self, descr, cls, name):
		
		self._model.rename_class_descriptor(descr, cls, name)
	
	def switch_order(self, cls1, cls2):
		
		self._model.switch_order(cls1, cls2)
	
	def del_class(self, name):
		
		self._model.del_class(name)
	
	def del_class_descriptor(self, descr, cls, class_only = False):
		
		self._model.del_class_descriptor(descr, cls, class_only)
	
	
	# ---- Import
	# ------------------------------------------------------------------------
	
	def add_data_row(self, 
		data: dict, 
		relations: set = set(), 
		unique: set = set(), 
		existing = {}, 
		return_added = False,
	):
		# add multiple objects with classes at once & automatically add relations 
		#	based on class relations or as specified in the relations attribute
		# data = {(Class name, Descriptor name): value, ...}
		# relations = {(Class name 1, label, Class name 2), ...}
		# unique = {Class name, ...}; always add a new object to classes 
		#	specified here, otherwise re-use objects with identical descriptors
		# existing = {Class name: Object, ...}
		#	use existing object for specified classes (i.e. just update descriptors)
		#
		# returns n_added or (n_added, added) if return_added == True
		#	added = {Class name: Object, ...}
		
		return self._model.add_data_row(
			data, relations, unique, existing, return_added
		)
	
	def import_data(self, get_data, n_rows, targets, relations, unique):
		# get_data(row, col) = value
		# targets = {col: (class_name, descriptor_name), ...}
		# relations = {(Class name 1, label, Class name 2), ...}
		# unique = {Class, ...}
		#
		# returns number of imported Objects
		
		n_added = 0
		for row in range(n_rows):
			data_row = {}  # {(Class name, Descriptor name): value, ...}
			for col in targets:
				value = try_numeric(get_data(row, col))
				if (value is None) or (value == ""):
					continue
				data_row[targets[col]] = value
			if data_row:
				n_added += self._model.add_data_row(data_row, relations, unique)
		return n_added
	
	def import_store(self, store, unique = set()):
		# unique = {Class name, ...}; always add a new object to classes 
		#	specified here, otherwise re-use objects with identical descriptors
		# progress = DProgress
		
		self._model.blockSignals(True)
		self._model.import_store(
			store, unique, progress = self._progress
		)
		self._model.blockSignals(False)
		self.on_changed(self._model.get_objects(), self._model.get_classes())
	
	
	# ---- User Tools
	# ------------------------------------------------------------------------
	def add_user_tool(self, user_tool):
		
		self._model.add_user_tool(user_tool)
	
	def get_user_tools(self):
		
		return self._model.get_user_tools()
	
	def del_user_tool(self, label):
		
		self._model.del_user_tool(label)
	
	
	# ---- Saved Query
	# ------------------------------------------------------------------------
	def add_saved_query(self, title, querystr):
		
		self._model.add_saved_query(title, querystr)
	
	def get_saved_query(self, title):
		
		return self._model.get_saved_query(title)
	
	def get_saved_queries(self):
		
		return self._model.get_saved_queries()
	
	def del_saved_query(self, title):
		
		self._model.del_saved_query(title)
	
	
	# ---- Persistence
	# ------------------------------------------------------------------------
	def has_auto_backup(self):
		
		return self._model.has_auto_backup()
	
	def set_auto_backup(self, state):
		
		self._model.set_auto_backup(state)
	
	def get_datasource(self):
		
		return self._model.get_datasource()
	
	def get_datasource_name(self):
		
		return self._model.get_datasource().get_name()
	
	def save(self, *args, **kwargs):
		
		if self._progress is not None:
			self._progress.show("Saving")
		if self._model.save(progress = self._progress, *args, **kwargs):
			if self._progress is not None:
				self._progress.stop()
			self.update_recent(kwargs)
			return True
		if self._progress is not None:
			self._progress.stop()
		return False
	
	def load(self, *args, **kwargs):
		# datasource = Datasource or format
		
		if self._progress is not None:
			self._progress.show("Loading")
		if self._model.load(progress = self._progress, *args, **kwargs):
			if self._progress is not None:
				self._progress.stop()
			self.update_recent(kwargs)
			return True
		if self._progress is not None:
			self._progress.stop()
		return False
	
	def is_saved(self):
		
		return self._model.is_saved()

