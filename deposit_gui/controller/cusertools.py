from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.view.vusertools import VUserTools

from deposit.utils.fnc_serialize import (load_user_tool, value_to_str)

from PySide2 import (QtCore)
from collections import defaultdict

class CUserTools(AbstractSubcontroller):
	
	def __init__(self, cmain, cview) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vusertools = VUserTools(cview._view, cmain.cmodel)
		self._vusertools.signal_search_submit.connect(self.on_search_submit)
		self._vusertools.signal_entry_submit.connect(self.on_entry_submit)
		self._vusertools.signal_entry_unlink.connect(self.on_entry_unlink)
		self._vusertools.signal_entry_remove.connect(self.on_entry_remove)
		self._vusertools.signal_import_tool.connect(self.on_import_tool)
		self._vusertools.signal_export_tool.connect(self.on_export_tool)
		self._vusertools.signal_add_tool.connect(self.on_add_tool)
		self._vusertools.signal_update_tool.connect(self.on_update_tool)
		self._vusertools.signal_del_tool.connect(self.on_del_tool)
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	@QtCore.Slot(str)
	def on_search_submit(self, querystr):
		
		self.cmain.cmdiarea.add_query(querystr)
	
	@QtCore.Slot(dict, dict, list, set)
	def on_entry_submit(self, values, objects_existing, relations, unique):
		#	values = {cls: {idx: {descr: value, ...}, ...}, ...}
		#	objects_existing = {cls: {idx: obj_id, ...}, ...}
		#	relations = [[cls1, rel, cls2], ...]
		#	unique = set(cls, ...)
		
		# create / find objects
		objects = defaultdict(dict) # {cls: {idx: obj_id, ...}, ...}
		for cls in values:
			for idx in values[cls]:
				if not (True in [(value is not None) for value in values[cls][idx].values()]):
					continue
				found = False
				if cls not in unique:
					cls_ = self.cmain.cmodel.add_class(cls)
					for obj in cls_.get_members():
						found = True
						for descr in values[cls][idx]:
							if value_to_str(obj.get_descriptor(descr)) != values[cls][idx][descr]:
								found = False
								break
						if found:
							break
				if found:
					objects[cls][idx] = obj
				else:
					if idx in objects_existing[cls]:
						objects[cls][idx] = self.cmain.cmodel.get_object(objects_existing[cls][idx])
					else:
						objects[cls][idx] = self.cmain.cmodel.add_class(cls).add_member()
					for descr in values[cls][idx]:
						objects[cls][idx].set_descriptor(descr, values[cls][idx][descr])
		
		# create relations
		for cls1, rel, cls2 in relations:
			if not ((cls1 in objects) and (cls2 in objects)):
				continue
			for idx1 in objects[cls1]:
				obj1 = objects[cls1][idx1]
				for idx2 in objects[cls2]:
					obj2 = objects[cls2][idx2]
					if obj1 == obj2:
						continue
					obj1.add_relation(obj2, rel)
	
	@QtCore.Slot(dict, list, set)
	def on_entry_unlink(self, objects_existing, relations, unique):
		#	objects_existing = {cls: {idx: obj_id, ...}, ...}
		#	relations = [[cls1, rel, cls2], ...]
		#	unique = set(cls, ...)
		
		obj_lookup = defaultdict(set)  # {cls: {obj_id, ...}, ...}
		existing_objs = set([])
		for cls in objects_existing:
			vals = objects_existing[cls].values()
			obj_lookup[cls].update(vals)
			existing_objs.update(vals)
		
		to_unlink = set([])  # {(obj_id1, rel, obj_id2), ...}
		for obj_id in obj_ids:
			obj = self.cmain.cmodel.get_object(obj_id)
			obj_classes = set(obj.get_classes())
			if unique.intersection(obj_classes):
				self.cmain.cmodel.del_object(obj_id)
			else:
				obj_relations = defaultdict(set)  # {rel: DObject, ...}
				for obj2, rel in obj.get_relations():
					obj_relations[rel].add(obj2)
				
				for cls1, rel, cls2 in relations:
					if not ((cls1 in unique) or (cls2 in unique)):
						continue
					if (cls2 in obj_classes) and (("~" + rel) in obj_relations):
						rel = "~" + rel
						cls1, cls2 = cls2, cls1
					if (cls1 in obj_classes) and (rel in obj_relations):
						for obj2 in obj.relations[rel]:
							if obj2 == obj:
								continue
							if obj2.id in existing_objs:
								if rel.startswith("~"):
									to_unlink.add((obj2, rel[1:], obj))
								else:
									to_unlink.add((obj, rel, obj2))
		for obj1, rel, obj2 in to_unlink:
			obj1.del_relation(obj2, rel)
	
	@QtCore.Slot(dict, set)
	def on_entry_remove(self, objects_existing, unique):
		#	objects_existing = {cls: {idx: obj_id, ...}, ...}
		#	unique = set(cls, ...)
		
		obj_ids = set([])
		for cls in objects_existing:
			obj_ids.update(objects_existing[cls].values())
		for obj_id in obj_ids:
			obj = self.cmain.cmodel.get_object(obj_id)
			if unique.intersection(obj.get_classes()):
				self.cmain.cmodel.del_object(obj_id)
	
	@QtCore.Slot()
	def on_import_tool(self):
		
		path, format = self.cmain.cview.get_load_path("Import User Tool", "(*.txt)")
		if path is None:
			return
		data = load_user_tool(path)
		self.cmain.cmodel.add_user_tool(data)
	
	@QtCore.Slot(object)
	def on_export_tool(self, user_tool):
		
		path, format = self.cmain.cview.get_save_path("Export User Tool", "(*.txt)")
		if path is None:
			return
		with open(path, "w", encoding = "utf-8") as f:
			f.write(user_tool.to_markup())
	
	@QtCore.Slot(object)
	def on_add_tool(self, user_tool):
		
		self.cmain.cmodel.add_user_tool(user_tool.to_dict())
	
	@QtCore.Slot(str, object)
	def on_update_tool(self, label, user_tool):
		
		self.cmain.cmodel.del_user_tool(label)
		self.cmain.cmodel.add_user_tool(user_tool.to_dict())
	
	@QtCore.Slot(str)
	def on_del_tool(self, label):
		
		self.cmain.cmodel.del_user_tool(label)
	
	@QtCore.Slot()
	def on_data_changed(self):
		
		self._vusertools.on_data_changed()
	
	def on_close(self):
		
		self._vusertools.on_close()
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	def populate_tools(self):
		
		self._vusertools.populate_tools(self.cmain.cmodel.get_user_tools())

