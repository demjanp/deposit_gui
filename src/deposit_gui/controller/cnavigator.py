from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.view.vnavigator import VNavigator

from PySide6 import (QtCore)

class CNavigator(AbstractSubcontroller):
	
	def __init__(self, cmain) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vnavigator = VNavigator()
		
		self._vnavigator.signal_widget_activated.connect(self.cmain.on_navigator_activated)
		self._vnavigator.signal_class_selected.connect(self.cmain.on_class_selected)
		self._vnavigator.signal_class_activated.connect(self.on_class_activated)
		self._vnavigator.signal_class_up.connect(self.on_class_up)
		self._vnavigator.signal_class_down.connect(self.on_class_down)
		self._vnavigator.signal_class_add.connect(self.on_class_add)
		self._vnavigator.signal_class_add_descriptor.connect(self.on_class_add_descriptor)
		self._vnavigator.signal_class_del_descriptor.connect(self.on_class_del_descriptor)
		self._vnavigator.signal_class_rename.connect(self.on_class_rename)
		self._vnavigator.signal_class_remove.connect(self.on_class_remove)
		
		self._vnavigator.signal_query_activated.connect(self.on_query_activated)
		self._vnavigator.signal_query_add.connect(self.on_query_add)
		self._vnavigator.signal_query_edit.connect(self.on_query_edit)
		self._vnavigator.signal_query_remove.connect(self.on_query_remove)
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	@QtCore.Slot(object, bool, object)
	def on_class_activated(self, cls, is_descriptor, parent_cls):
		
		if cls == "!*":
			querystr = "SELECT !*"
		elif not is_descriptor:
			querystr = "SELECT [%s].*" % (cls.name)
		else:
			return
		self.cmain.cmdiarea.add_query(querystr)
	
	@QtCore.Slot(object, object)
	def on_class_up(self, cls, cls_above):
		
		self.cmain.cmodel.switch_order(cls, cls_above)
	
	@QtCore.Slot(object, object)
	def on_class_down(self, cls, cls_below):
		
		self.cmain.cmodel.switch_order(cls, cls_below)
	
	@QtCore.Slot(object, bool, object)
	def on_class_add(self, cls, is_descriptor, parent_cls):
		
		if is_descriptor:
			cls = None
		self.cmain.cdialogs.open("AddClass", cls)
	
	@QtCore.Slot(object, bool, object)
	def on_class_add_descriptor(self, cls, is_descriptor, parent_cls):
		
		if is_descriptor:
			return
		self.cmain.cdialogs.open("AddDescriptor", cls)
	
	@QtCore.Slot(object, bool, object)
	def on_class_del_descriptor(self, cls, is_descriptor, parent_cls):
		
		if not is_descriptor:
			return
		self.cmain.cdialogs.open("DelDescriptor", cls, parent_cls)
	
	@QtCore.Slot(object, bool, object)
	def on_class_rename(self, cls, is_descriptor, parent_cls):
		
		self.cmain.cdialogs.open("RenameClass", cls, is_descriptor, parent_cls)
	
	@QtCore.Slot(object)
	def on_class_remove(self, classes):
		
		self.cmain.cdialogs.open("DelClass", classes)
	
	@QtCore.Slot(str)
	def on_query_activated(self, title):
		
		self.cmain.cmdiarea.add_query(self.cmain.cmodel.get_saved_query(title))
	
	@QtCore.Slot()
	def on_query_add(self):
		
		self.cmain.cdialogs.open("AddSavedQuery")
	
	@QtCore.Slot(str)
	def on_query_edit(self, title):
		
		self.cmain.cdialogs.open("EditSavedQuery", title)
	
	@QtCore.Slot(list)
	def on_query_remove(self, titles):
		
		self.cmain.cdialogs.open("RemoveSavedQuery", titles)
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	def populate_classes(self):
		
		descriptors = self.cmain.cmodel.get_descriptor_names()
		classes = [cls for cls in self.cmain.cmodel.get_classes() if cls.name not in descriptors]
		self._vnavigator.populate_classes(classes)
	
	def populate_queries(self):
		
		self._vnavigator.populate_queries(self.cmain.cmodel.get_saved_queries())
	
	
	def deselect_all(self):
		
		self._vnavigator.deselect_all()

