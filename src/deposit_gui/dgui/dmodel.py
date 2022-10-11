from deposit import Store
from deposit.store.dobject import DObject
from deposit.store.dclass import DClass

from deposit_gui.utils.fnc_thumbnails import (load_thumbnails, get_thumbnail)
from deposit.utils.fnc_files import (get_temp_path, sanitize_filename)

from PySide2 import (QtCore)
import shutil
import uuid
import os

class DModel(QtCore.QObject):
	
	signal_store_event = QtCore.Signal(int, list, list, object)
	# event, objects, classes, datasource
	
	EVENT_ADDED =					0x00000000
	EVENT_DELETED =					0x00000100
	EVENT_CHANGED =					0x00000200
	EVENT_SAVED =					0x00000400
	EVENT_LOADED =					0x00000800
	EVENT_LOCAL_FOLDER_CHANGED =	0x00001000
	EVENT_QUERIES_CHANGED =			0x00002000
	EVENT_USER_TOOLS_CHANGED =		0x00004000
	EVENT_SETTINGS_CHANGED =		0x00008000
	
	def __init__(self, store = None):
		
		QtCore.QObject.__init__(self)
		
		self._store = Store() if store is None else store
		self._thumbnail_cache = {}
		
		self._store.set_callback_added(self.on_added)
		self._store.set_callback_deleted(self.on_deleted)
		self._store.set_callback_changed(self.on_changed)
		self._store.set_callback_saved(self.on_saved)
		self._store.set_callback_loaded(self.on_loaded)
		self._store.set_callback_local_folder_changed(self.on_local_folder_changed)
		self._store.set_callback_queries_changed(self.on_queries_changed)
		self._store.set_callback_user_tools_changed(self.on_user_tools_changed)
		self._store.set_callback_settings_changed(self.on_settings_changed)
	
	def _to_objects_and_classes(self, elements):
		
		objects = []
		classes = []
		for element in elements:
			if isinstance(element, DObject) or isinstance(element, int):
				objects.append(element)
			elif isinstance(element, DClass) or isinstance(element, str):
				classes.append(element)
		return objects, classes
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	def on_added(self, elements):
		# elements = [DObject, DClass, ...]
		
		objects, classes = self._to_objects_and_classes(elements)
		self.signal_store_event.emit(self.EVENT_ADDED, objects, classes, None)
	
	def on_deleted(self, elements):
		# elements = [obj_id, name, ...]
		
		objects, classes = self._to_objects_and_classes(elements)
		self.signal_store_event.emit(self.EVENT_DELETED, objects, classes, None)
	
	def on_changed(self, elements):
		# elements = [DObject, DClass, ...]
		
		objects, classes = self._to_objects_and_classes(elements)
		self.signal_store_event.emit(self.EVENT_CHANGED, objects, classes, None)
	
	def on_saved(self, datasource):
		
		self.signal_store_event.emit(self.EVENT_SAVED, [], [], datasource)
	
	def on_loaded(self):
		
		self.signal_store_event.emit(self.EVENT_LOADED, [], [], None)
	
	def on_local_folder_changed(self):
		
		self.signal_store_event.emit(self.EVENT_LOCAL_FOLDER_CHANGED, [], [], None)
	
	def on_queries_changed(self):
		
		self.signal_store_event.emit(self.EVENT_QUERIES_CHANGED, [], [], None)
	
	def on_user_tools_changed(self):
		
		self.signal_store_event.emit(self.EVENT_USER_TOOLS_CHANGED, [], [], None)
	
	def on_settings_changed(self):
		
		self.signal_store_event.emit(self.EVENT_SETTINGS_CHANGED, [], [], None)
	
	
	# ---- General
	# ------------------------------------------------------------------------
	def clear(self) -> None:
		
		self._thumbnail_cache = {}
		self._store.clear()
	
	def get_updated_url(self, resource):
		
		return self._store.get_updated_url(resource)
	
	def set_local_folder(self, path, progress = None):
		
		self._store.set_local_folder(path, progress)
	
	def has_local_folder(self):
		
		return self._store.has_local_folder()
	
	def get_folder(self):
		
		return self._store.get_folder()
	
	def get_resource_urls(self):
		
		return self._store.get_resource_urls()
	
	def prune_resources(self):
		
		self._store.prune_resources()
	
	def open_resource(self, resource):
		# resource = DResource
		
		return self._store.open_resource(resource)
	
	def get_temp_folder(self, name, appdir = "deposit"):
		
		return get_temp_path(name, appdir = appdir)
	
	def get_temp_copy(self, resource, appdir = "deposit"):
		
		source = self.open_resource(resource)
		if source is None:
			return None
		filename = sanitize_filename(resource.filename)
		tgt_path = os.path.join(
			get_temp_path(uuid.uuid4().hex, appdir = appdir),
			filename,
		)
		target = open(tgt_path, "wb")
		shutil.copyfileobj(source, target)
		source.close()
		target.close()
		
		return tgt_path
	
	
	# ---- Create
	# ------------------------------------------------------------------------
	def add_object(self):
		
		return self._store.add_object()
	
	def add_class(self, name):
		
		return self._store.add_class(name)
	
	def add_user_tool(self, user_tool):
		
		self._store.add_user_tool(user_tool)
	
	def add_saved_query(self, title, querystr):
		
		self._store.add_saved_query(title, querystr)
	
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
		
		return self._store.add_data_row(data, relations, unique, existing, return_added)
	
	def import_store(self, store, unique = set(), progress = None):
		# unique = {Class name, ...}; always add a new object to classes 
		#	specified here, otherwise re-use objects with identical descriptors
		# progress = DProgress
		
		self._store.import_store(store, unique, progress)
	
	
	# ---- Read
	# ------------------------------------------------------------------------
	def get_object(self, obj_id: int):
		
		return self._store.get_object(obj_id)
	
	def get_objects(self) -> set:
		# return {DObject, ...}
		
		return self._store.get_objects()
	
	def get_object_ids(self) -> set:
		
		return self._store.get_object_ids()
	
	
	def get_class(self, name):
		
		return self._store.get_class(name)
	
	def get_classes(self, ordered = False) -> list:
		# return [DClass, ...]
		
		return self._store.get_classes(ordered)
	
	def get_class_names(self, ordered = False) -> list:
		# return [name, ...]
		
		return self._store.get_class_names(ordered)
	
	def has_class(self, name) -> bool:
		
		return self._store.has_class(name)
	
	
	def get_descriptors(self, ordered = False) -> list:
		# return [DClass, ...]
		
		return self._store.get_descriptors(ordered)
	
	def get_descriptor_names(self, ordered = False) -> list:
		# return [name, ...]
		
		return self._store.get_descriptor_names(ordered)
	
	def get_descriptor_values(self, class_name, descriptor_name, direct_only = True) -> list:
		# direct_only = if True, don't return members of subclasses
		#
		# returns [value, ...]
		
		return self._store.get_descriptor_values(class_name, descriptor_name, direct_only)
	
	
	def get_user_tools(self):
		
		return self._store.get_user_tools()
	
	
	def get_saved_query(self, title):
		
		return self._store.get_saved_query(title)
	
	def get_saved_queries(self):
		
		return self._store.get_saved_queries()
	
	
	def get_relation_labels(self) -> set:
		
		return self._store.get_relation_labels()
	
	
	def get_query(self, querystr, **kwargs):
		
		return self._store.get_query(querystr, **kwargs)
	
	
	def get_subgraph(self, objects, progress):
		
		return self._store.get_subgraph(objects, progress)
	
	
	def get_thumbnail(self, resource, size = 256):
		
		folder = self.get_folder()
		if folder is None:
			return None
		return get_thumbnail(resource, folder, self._thumbnail_cache, size)
	
	
	# ---- Update
	# ------------------------------------------------------------------------
	def switch_order(self, cls1, cls2) -> None:
		
		self._store.switch_order(cls1, cls2)
	
	def rename_class(self, cls, name):
		
		cls.rename(name)
	
	def rename_class_descriptor(self, descr, cls, name):
		
		if cls.has_descriptor(descr):
			cls.del_descriptor(descr)
			cls.set_descriptor(name)
		for obj in cls.get_members():
			obj.rename_rescriptor(descr, name)
	
	
	# ---- Delete
	# ------------------------------------------------------------------------
	def del_object(self, obj_id) -> None:
		
		self._store.del_object(obj_id)
	
	def del_class(self, name) -> None:
		
		self._store.del_class(name)
	
	def del_user_tool(self, label):
		
		self._store.del_user_tool(label)
	
	def del_class_descriptor(self, descr, cls, class_only = True):
		
		descr = self.get_class(descr)
		cls = self.get_class(cls)
		if (descr is None) or (cls is None):
			return
		cls.del_descriptor(descr)
		if class_only:
			return
		for obj in cls.get_members():
			obj.del_descriptor(descr)
	
	def del_saved_query(self, title):
		
		self._store.del_saved_query(title)
	
	
	# ---- Persistence
	# ------------------------------------------------------------------------
	def init_datasource(self, format):
		# format = Datasource or format
		
		return self._store.init_datasource(format)
	
	def has_auto_backup(self):
		
		return self._store.has_auto_backup()
	
	def set_auto_backup(self, state):
		
		self._store.set_auto_backup(state)
	
	def get_datasource(self):
		
		return self._store.get_datasource()
	
	def set_datasource(self, datasource):
		
		self._store.set_datasource(datasource)
	
	def save(self, *args, **kwargs):
		# datasource = Datasource or format
		
		return self._store.save(*args, **kwargs)
	
	def load(self, *args, **kwargs):
		# datasource = Datasource or format
		
		ret = self._store.load(*args, **kwargs)
		if not ret:
			return False
		load_thumbnails(self.get_folder(), self._thumbnail_cache)
		
		return True
	
	def is_saved(self):
		
		return self._store.is_saved()


