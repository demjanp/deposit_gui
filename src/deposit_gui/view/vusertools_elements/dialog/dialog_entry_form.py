from deposit_gui.view.vusertools_elements.dialog.dialog_form import (DialogForm)

from deposit.utils.fnc_serialize import (value_to_str)

from PySide6 import (QtWidgets, QtCore)
from collections import defaultdict
from natsort import natsorted

class DialogEntryForm(DialogForm):
	
	signal_submit = QtCore.Signal(dict, dict, list, set, dict)
	#	values, objects_existing, relations, unique, objects_loaded
	signal_unlink = QtCore.Signal(dict, list, set, list)
	#	objects_existing, relations, unique, obj_ids
	signal_remove = QtCore.Signal(dict, set)
	#	objects_existing, unique
	#		values = {cls: {idx: {descr: value, ...}, ...}, ...}
	#		objects_existing = {cls: {idx: obj_id, ...}, ...}
	#		relations = [[cls1, rel, cls2], ...]
	#		unique = set(cls, ...)
	
	def __init__(self, vusertools, form_tool, selected_id):
		
		DialogForm.__init__(self, vusertools, form_tool)
		
		self.selected_id = selected_id
		self.objects_loaded = {}
		
		if self._vusertools.entry_form_geometry is not None:
			self.setGeometry(self._vusertools.entry_form_geometry)
		else:
			self.setMinimumWidth(600)
		
		self.overrideWindowFlags(QtCore.Qt.WindowType.Window)
		
		button_remove = QtWidgets.QPushButton("Delete")
		button_remove.clicked.connect(self.on_remove)
		self.button_frame.layout().addWidget(button_remove)
		
		if self.selected_id is not None:
			self.populate()
	
	def find_relations(self):
		# find all possible relations
		# returns frames, framesets, relations
		# frames = [DialogFrame(), ...]
		# framesets = [[DialogFrame(), ...], ...]
		# relations = [[cls1, rel, cls2], ...]
		
		relations = []  # [[cls1, rel, cls2], ...]
		classes = set()
		frames, framesets = self.frames()
		for frame in frames:
			classes.add(frame.dclass)
		for frameset in framesets:
			for frame in frameset:
				classes.add(frame.dclass)
		for cls1 in classes:
			cls1 = self._vusertools._cmodel.get_class(cls1)
			if cls1 is None:
				continue
			for cls2, rel in cls1.get_relations():
				if rel.startswith("~"):
					continue
				if cls2 == cls1:
					continue
				if cls2.name not in classes:
					continue
				relations.append([cls1.name, rel, cls2.name])
		relations = natsorted(relations)
		
		return frames, framesets, relations
	
	def populate(self):
		
		self.clear()
		
		# find all possible relations
		frames, framesets, relations = self.find_relations()
		collect = []
		for cls1, rel, cls2 in relations:
			rel_rev = self._vusertools._cmodel.reverse_relation(rel)
			collect.append([cls2, rel_rev, cls1])
		relations += collect
		
		# find classes from multi groups
		multi_classes = defaultdict(set)  # {cls: set(group, ...), ...}
		for group in self.multigroups():
			for frameset in group.framesets():
				for frame in frameset:
					multi_classes[frame.dclass].add(group)
		
		# get all relevant objects
		objects = defaultdict(list)  # {class: [object, ...], ...}
		obj = self._vusertools._cmodel.get_object(self.selected_id)
		if obj is None:
			return
		for cls in obj.get_class_names():
			objects[cls].append(obj)
		while True:
			found = False
			for cls1, rel, cls2 in relations:
				if cls1 in objects:
					for obj1 in objects[cls1]:
						for obj2, rel in obj1.get_relations():
							classes2 = obj2.get_class_names()
							if set(obj1.get_class_names()).intersection(classes2):
								continue
							if (cls2 in classes2) and ((cls2 in multi_classes) or (cls2 not in objects)) and (obj2 not in objects[cls2]):
								objects[cls2].append(obj2)
								found = True
			if not found:
				break
		
		# collect data from objects
		data = {}  # {cls: {obj_id: {descr: value, ...}, ...}, ...}
		for cls in objects:
			data[cls] = {}
			for obj in objects[cls]:
				data[cls][obj.id] = {}			
				for descr in obj.get_descriptors():
					value = value_to_str(obj.get_descriptor(descr))
					if value is None:
						continue
					data[cls][obj.id][descr.name] = value
		
		# fill single entry frames
		for frame in frames:
			if frame.dclass not in data:
				continue
			obj_id = next(iter(data[frame.dclass]))
			if frame.descriptor in data[frame.dclass][obj_id]:
				frame.set_value(data[frame.dclass][obj_id][frame.descriptor], obj_id)
		
		# fill multi entry fields
		group_ids = defaultdict(set)  # {obj_id: set(group, ...), ...}
		frameset_values = defaultdict(lambda: defaultdict(dict))  # {obj_id: {cls: {descriptor: value, ...}, ...}, ...}
		for cls in multi_classes:
			if cls not in data:
				continue
			for obj_id in data[cls]:
				group_ids[obj_id].update(multi_classes[cls])
				for descr in data[cls][obj_id]:
					value = data[cls][obj_id][descr]
					if value is not None:
						frameset_values[obj_id][cls][descr] = value
		for obj_id in frameset_values:
			for group in group_ids[obj_id]:
				frameset = group.framesets()[-1]
				for frame in frameset:
					if (frame.dclass in frameset_values[obj_id]) and (frame.descriptor in frameset_values[obj_id][frame.dclass]):
						frame.set_value(frameset_values[obj_id][frame.dclass][frame.descriptor], obj_id)
				group.add_entry()
		self.adjust_labels()
		
		_, objects_existing, _ = self.get_data()
		self.objects_loaded = dict([(cls, list(objects_existing[cls].values())) for cls in objects_existing])
	
	def get_data(self):
		
		# find frames, framesets and all possible relations
		frames, framesets, relations = self.find_relations()
		# frames = [DialogFrame(), ...]
		# framesets = [[DialogFrame(), ...], ...]
		# relations = [[cls1, rel, cls2], ...]
		
		# collect values from form
		values = defaultdict(lambda: defaultdict(dict))  # {cls: {idx: {descr: value, ...}, ...}, ...}
		objects_existing = defaultdict(dict)  # {cls: {idx: obj_id, ...}, ...}
		for frame in frames:
			value = frame.get_value()
			if value == "":
				value = None
			values[frame.dclass][0][frame.descriptor] = value
			obj_id = frame.get_object()
			if obj_id is not None:
				objects_existing[frame.dclass][0] = obj_id
		idx = -1
		for frameset in framesets:
			idx += 1
			for frame in frameset:
				value = frame.get_value()
				if value == "":
					value = None
				values[frame.dclass][idx][frame.descriptor] = value
				obj_id = frame.get_object()
				if obj_id is not None:
					objects_existing[frame.dclass][idx] = obj_id
		
		return values, objects_existing, relations
	
	def clear(self):
		
		for group in self.multigroups():
			group.clear()
		frames, _ = self.frames()
		for frame in frames:
			frame.set_value("")
	
	@QtCore.Slot(list)
	def on_entry_removed(self, obj_ids):
		
		if not obj_ids:
			return
		_, objects_existing, relations = self.get_data()
		
		self.signal_unlink.emit(objects_existing, relations, self.unique, obj_ids)
		self.clear()
		self.populate()
	
	@QtCore.Slot()
	def on_submit(self):
		
		values, objects_existing, relations = self.get_data()
		self.signal_submit.emit(values, objects_existing, relations, self.unique, self.objects_loaded)
		self.clear()
	
	@QtCore.Slot()
	def on_reset(self):
		
		self.clear()
	
	@QtCore.Slot()
	def on_remove(self):
		
		if not self.unique:
			return
		_, objects_existing, _ = self.get_data()  # {cls: {idx: obj_id, ...}, ...}
		self.selected_id = None
		self.clear()
		self.signal_remove.emit(objects_existing, self.unique)
		self.populate()
	
	def closeEvent(self, event):
		
		self._vusertools.entry_form_geometry = self.geometry()
		DialogForm.closeEvent(self, event)

