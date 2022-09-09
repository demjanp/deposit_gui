from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.view.vnavigator_elements.class_widget import ClassWidget
from deposit_gui.view.vnavigator_elements.query_widget import QueryWidget

from PySide2 import (QtWidgets, QtCore, QtGui)

class VNavigator(AbstractSubview, QtWidgets.QFrame):
	
	signal_widget_activated = QtCore.Signal()
	
	signal_class_selected = QtCore.Signal(list)					# [DClass, ...]
	signal_class_activated = QtCore.Signal(object, bool, object)# DClass, is_descriptor, parent DClass
	signal_class_up = QtCore.Signal(object, object)				# DClass, DClass above
	signal_class_down = QtCore.Signal(object, object)			# DClass, DClass below
	signal_class_add = QtCore.Signal(object, bool, object)		# DClass, is_descriptor, parent DClass
	signal_class_add_descriptor = QtCore.Signal(object, bool, object)	# DClass, is_descriptor, parent DClass
	signal_class_del_descriptor = QtCore.Signal(object, bool, object)	# DClass, is_descriptor, parent DClass
	signal_class_rename = QtCore.Signal(object, bool, object)	# DClass, is_descriptor, parent DClass
	signal_class_remove = QtCore.Signal(list)					# [DClass, ...]
	
	signal_query_activated = QtCore.Signal(str)					# title
	signal_query_add = QtCore.Signal()
	signal_query_edit = QtCore.Signal(str)						# title
	signal_query_remove = QtCore.Signal(list)					# [title, ...]
	
	def __init__(self) -> None:
		
		AbstractSubview.__init__(self)
		QtWidgets.QFrame.__init__(self)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
		
		toolbox = QtWidgets.QToolBox()
		toolbox.layout().setSpacing(0)
		toolbox.setStyleSheet('''
			QToolBox {
				icon-size: 32px;
			}
			QToolBox::tab {
				font: bold;
			}
		''')
		
		self.layout().addWidget(toolbox)
		
		self._classwidget = ClassWidget(self)
		self._querywidget = QueryWidget(self)
		
		toolbox.addItem(self._classwidget, self.get_icon("class.svg"), "Classes")
		toolbox.addItem(self._querywidget, self.get_icon("query.svg"), "Queries")
	
	def populate_classes(self, classes):
		
		self._classwidget.populate(classes)
	
	def populate_queries(self, queries):
		
		self._querywidget.populate(queries)
	
	
	def deselect_all(self):
		
		self._classwidget.deselect_all()
	
	def _get_one_selected_class(self):
		# returns class, is_descriptor, parent_class
		
		cls = self._classwidget.get_selected()
		if len(cls) == 1:
			is_descriptor = self._classwidget.get_selected_is_descriptor()
			parent = self._classwidget.get_selected_parent()
			return cls[0], is_descriptor, parent
		return None, None, None
	
	
	@QtCore.Slot(list)
	def on_class_selected(self, classes):
		
		self._classwidget.update_footer()
		self.signal_class_selected.emit(classes)
	
	@QtCore.Slot(object, bool, object)
	def on_class_activated(self, cls, is_descriptor, parent_cls):
		
		self.signal_class_activated.emit(cls, is_descriptor, parent_cls)
	
	@QtCore.Slot()
	def on_widget_activated(self):
		
		self.signal_widget_activated.emit()
	
	@QtCore.Slot()
	def on_class_up(self):
		
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		if cls:
			above, _ = self._classwidget.get_items_around_selected()
			if above:
				self._classwidget.select_one_above()
				self.signal_class_up.emit(cls, above)
	
	@QtCore.Slot()
	def on_class_down(self):
		
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		if cls:
			_, below = self._classwidget.get_items_around_selected()
			if below:
				self._classwidget.select_one_below()
				self.signal_class_down.emit(cls, below)
	
	@QtCore.Slot()
	def on_class_add(self):
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		self.signal_class_add.emit(cls, is_descriptor, parent_cls)
	
	@QtCore.Slot()
	def on_class_add_descriptor(self):
		
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		self.signal_class_add_descriptor.emit(cls, is_descriptor, parent_cls)
	
	@QtCore.Slot()
	def on_class_del_descriptor(self):
		
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		self.signal_class_del_descriptor.emit(cls, is_descriptor, parent_cls)
	
	@QtCore.Slot()
	def on_class_rename(self):
		
		cls, is_descriptor, parent_cls = self._get_one_selected_class()
		if cls:
			self.signal_class_rename.emit(cls, is_descriptor, parent_cls)
	
	@QtCore.Slot()
	def on_class_remove(self):
		
		classes = self._classwidget.get_selected()
		if classes:
			self.signal_class_remove.emit(classes)
	
	
	@QtCore.Slot(list)
	def on_query_selected(self, queries):
		
		self._querywidget.update_footer()
	
	@QtCore.Slot(str)
	def on_query_activated(self, title):
		
		self.signal_query_activated.emit(title)
	
	@QtCore.Slot()
	def on_query_add(self):
		
		self.signal_query_add.emit()
	
	@QtCore.Slot()
	def on_query_edit(self):
		
		selected = self._querywidget.get_selected()
		if selected:
			self.signal_query_edit.emit(selected[0])
	
	@QtCore.Slot()
	def on_query_remove(self):
		
		selected = self._querywidget.get_selected()
		if selected:
			self.signal_query_remove.emit(selected)

