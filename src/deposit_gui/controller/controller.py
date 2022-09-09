from deposit_gui.controller.cmodel import CModel
from deposit_gui.controller.cview import CView
from deposit_gui.controller.cdialogs import CDialogs
from deposit_gui.controller.cnavigator import CNavigator
from deposit_gui.controller.cmdiarea import CMDIArea
from deposit_gui.controller.cactions import CActions
from deposit_gui.controller.cquerytoolbar import CQueryToolbar
from deposit_gui.controller.cusertools import CUserTools


from deposit import Store

from PySide2 import (QtWidgets, QtCore, QtGui)
import sys
import os

class Controller(QtCore.QObject):
	
	signal_selection_changed = QtCore.Signal()
	
	def __init__(self, store):
		
		QtCore.QObject.__init__(self)
		
		self._selected_objects = set()
		self._selected_classes = set()
		self._selected_relations = []
		self._selected_queryitems = set()
		
		self._is_subwindow = (store is not None)
		
		self.cmodel = CModel(self, store)
		self.cnavigator = CNavigator(self)
		self.cmdiarea = CMDIArea(self)
		self.cview = CView(self, self.cnavigator, self.cmdiarea)
		self.cdialogs = CDialogs(self, self.cview)
		self.cactions = CActions(self, self.cview)
		self.cquerytoolbar = CQueryToolbar(self, self.cview)
		self.cusertools = CUserTools(self, self.cview)
		
		self.cmodel.on_loaded()
		self.cview.log_message("Deposit GUI started")
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	@QtCore.Slot()
	def on_navigator_activated(self):
		
		self.cmdiarea.deselect_all()
	
	@QtCore.Slot(bool)
	def on_mdiarea_activated(self, state):
		
		if state:
			self.cnavigator.deselect_all()
		self.cactions.update()
	
	@QtCore.Slot(list)
	def on_class_selected(self, classes):
		
		self._selected_queryitems = set()
		self._selected_objects = set()
		self._selected_classes = set(classes)
		self._selected_relations = []
		self.on_selection_changed()
	
	@QtCore.Slot(list)
	def on_object_selected(self, objects):
		
		self._selected_queryitems = set()
		self._selected_objects = set(objects)
		self._selected_classes = set()
		self._selected_relations = []
		self.on_selection_changed()
	
	@QtCore.Slot(list)
	def on_query_selected(self, items):
		
		self._selected_queryitems = set(items)
		self._selected_objects = set()
		self._selected_classes = set()
		self._selected_relations = []
		for item in self._selected_queryitems:
			if item.obj_id is not None:
				self._selected_objects.add(self.cmodel.get_object(item.obj_id))
		self.on_selection_changed()
	
	@QtCore.Slot(list)
	def on_relation_selected(self, relations):
		# relations = [(Source, Target, label), ...]
		
		self._selected_queryitems = set()
		self._selected_objects = set()
		self._selected_classes = set()
		self._selected_relations = relations
		self.on_selection_changed()
	
	def on_selection_changed(self):
		
		self.cactions.update()
		self.signal_selection_changed.emit()
	
	def on_close(self):
		
		if not self.check_save():
			return False
			
		self.cusertools.on_close()
		return True
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	def get_selected_queryitems(self):
		# returns set(QueryItem, ...)
		
		return self._selected_queryitems
	
	def get_selected_objects(self):
		# returns set(DObject, ...)
		
		return self._selected_objects
	
	def get_selected_classes(self):
		# returns set(DClass, ...)
		
		return self._selected_classes
	
	def get_selected_relations(self):
		
		return self._selected_relations
	
	
	def check_save(self):
		
		if (not self._is_subwindow) and (not self.cmodel.is_saved()):
			reply = QtWidgets.QMessageBox.question(self.cview._view, 
				"Exit", "Save changes to database?",
				QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel
			)
			if reply == QtWidgets.QMessageBox.Yes:
				self.cactions.on_Save(True)
			elif reply == QtWidgets.QMessageBox.No:
				return True
			else:
				return False
		
		return True
	
	
	def open_in_external(self, path):
		
		if sys.platform in ["linux", "linux2", "darwin"]:
			return # TODO		
		if sys.platform.startswith("win"):
			if os.path.isfile(path):
				os.startfile(path)

	
	def close(self):
		
		self.cview.close()
