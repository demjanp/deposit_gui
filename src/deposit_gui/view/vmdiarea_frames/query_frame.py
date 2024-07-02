from deposit_gui.view.vmdiarea_frames.abstract_mdiarea_frame import AbstractMDIAreaFrame
from deposit_gui.view.vmdiarea_frames.query_frame_elements.relation_frame import RelationFrame
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_tab_table import QueryTabTable
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_tab_images import (QueryTabImagesLazy, QueryTabImages)
from deposit_gui.view.vmdiarea_frames.query_frame_elements.query_tab_graph import (QueryTabGraphLazy, QueryTabGraph)

from PySide6 import (QtWidgets, QtCore, QtGui)

class QueryFrame(AbstractMDIAreaFrame, QtWidgets.QFrame):
	
	signal_query_selected = QtCore.Signal(list)		# [QueryItem, ...]
	signal_query_activated = QtCore.Signal(object)	# QueryItem
	signal_object_selected = QtCore.Signal(list)	# [DObject, ...]
	signal_relation_selected = QtCore.Signal(list)	# [(Source, Target, label), ...]
	signal_add_object = QtCore.Signal(object)		# Query
	signal_del_object = QtCore.Signal()
	signal_del_descriptor = QtCore.Signal()
	signal_add_class = QtCore.Signal()
	signal_del_class = QtCore.Signal(object)		# Query
	signal_edited = QtCore.Signal(object, object)	# QueryItem, value
	signal_drop_url = QtCore.Signal(object, str)	# QueryItem, url
	
	# signal_class_link = QtCore.Signal(str)				# class_name
	# signal_relation_link = QtCore.Signal(int, str, str)	# obj_id, rel_label, class_name
	# signal_relation_unlink = QtCore.Signal(int, str, str)	# obj_id, rel_label, class_name
	
	
	INITIAL_THUMBNAIL_SIZE = 128
	
	def __init__(self, query, cmodel, cview):
		
		AbstractMDIAreaFrame.__init__(self)
		QtWidgets.QFrame.__init__(self)
		
		self._query = query
		self._cmodel = cmodel
		self._cview = cview
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		
		self.relation_frame = RelationFrame()
		self.relation_frame.signal_object_link.connect(self.on_object_link)
		self.signal_class_link = self.relation_frame.signal_class_link
		self.signal_relation_link = self.relation_frame.signal_relation_link
		self.signal_relation_unlink = self.relation_frame.signal_relation_unlink
		
		self.footer = QueryFooter(self)
		
		self.tab_table = QueryTabTable(self)
		self.tab_images = QueryTabImagesLazy(self)
		self.tab_graph = QueryTabGraphLazy(self)
		
		self.tabs = QtWidgets.QTabWidget()
		self.tabs.addTab(self.tab_table, "Table")
		self.tabs.addTab(self.tab_images, "Images")
		self.tabs.addTab(self.tab_graph, "Graph")
		
		splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
		splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.layout().addWidget(splitter)
		
		frame_left = QtWidgets.QFrame()
		frame_left_layout = QtWidgets.QVBoxLayout()
		frame_left.setLayout(frame_left_layout)
		frame_left.layout().setContentsMargins(0, 0, 0, 0)
		frame_left.layout().setSpacing(0)
		frame_left.layout().addWidget(self.tabs)
		frame_left.layout().addWidget(self.footer)

		self.scroll_area = QtWidgets.QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setFrameStyle(QtWidgets.QFrame.NoFrame)
		self.scroll_area.setWidget(self.relation_frame)
		
		splitter.addWidget(frame_left)
		splitter.addWidget(self.scroll_area)
		
		self._filter_timer = QtCore.QTimer()
		self._filter_timer.setSingleShot(True)
		self._filter_timer.timeout.connect(self.on_filter_timer)
		
		self.footer.set_object_buttons_enabled(self._query.main_class != "*")
		self.footer.set_del_object_enabled(False)
		
		self.tabs.currentChanged.connect(self.on_tab_changed)
		
		self.update_count()
	
	def title(self):
		
		return self._query.querystr
	
	def icon(self):
		
		return "dep_cube.svg"
	
	def update_query(self, objects = None, classes = None):
		
		if  ((objects is None) and (classes is None)) or \
			("*" in self._query.classes) or \
			(self._query.main_class is None) or \
			set(self._query.classes).intersection([
				cls if isinstance(cls, str) else cls.name for cls in classes
			]) or self._query.objects.intersection([
				obj if isinstance(obj, int) else obj.id for obj in objects
			]):
			
			current_index = self.tabs.currentIndex()
			if current_index > 0:
				self.tabs.setCurrentIndex(0)
			
			self._query.process()
			self._cview.progress.stop()
			
			self.tab_table.update_query()
			self.relation_frame.populate()
			if isinstance(self.tab_images, QueryTabImages):
				self.tab_images.update_query(
					self.tab_table.get_images(), self.tab_table.get_item_order()
				)
			if isinstance(self.tab_graph, QueryTabGraph):
				self.tab_graph.update_query()
			
			if current_index > 0:
				self.tabs.setCurrentIndex(current_index)
	
	def select_all(self):
		
		self.get_current_tab().selectAll()
	
	def clear_selection(self):
		
		self.get_current_tab().clearSelection()
	
	def populate_tab_images(self):
		
		if isinstance(self.tab_images, QueryTabImages):
			return
		
		self.tab_images = QueryTabImages(self, self.tab_table.get_images(), self.tab_table.get_item_order(), self._cmodel)
		self.tab_images.set_thumbnail_size(self.INITIAL_THUMBNAIL_SIZE)
		self.tabs.blockSignals(True)
		self.tabs.insertTab(1, self.tab_images, "Images")
		self.tabs.removeTab(2)
		self.tabs.setCurrentIndex(1)
		self.tabs.blockSignals(False)
	
	def populate_tab_graph(self):
		
		if isinstance(self.tab_graph, QueryTabGraph):
			return
		self.tab_graph = QueryTabGraph(self)
		self.tabs.blockSignals(True)
		self.tabs.insertTab(2, self.tab_graph, "Graph")
		self.tabs.removeTab(3)
		self.tabs.setCurrentIndex(2)
		self.tabs.blockSignals(False)
	
	def get_current_tab(self):
		
		return [self.tab_table, self.tab_images, self.tab_graph][self.tabs.currentIndex()]
	
	def update_count(self):
		
		self.footer.set_count(self.get_current_tab().get_row_count())
	
	def get_header(self, col, user_role = False):
		# pass to deposit.AbstractExternalsource to provide header data from QueryTabTable
		
		return self.tab_table._table_model.headerData(col, QtCore.Qt.Horizontal, QtCore.Qt.UserRole if user_role else QtCore.Qt.DisplayRole)
	
	def get_item(self, row, col):
		# pass to deposit.AbstractExternalsource to provide data from QueryTabTable
		
		return self.tab_table.get_item(row, col)
	
	def get_row_count(self):
		
		return self.tab_table.get_row_count()
	
	def get_column_count(self):
		
		return self.tab_table.get_column_count()
	
	def get_object(self, obj_id):
		
		return self._cmodel.get_object(obj_id)
	
	def get_data(self):
		# returns data = {obj_id: {(class, descriptor): value, ...}, ...}
		
		data = {}
		for row in range(self.get_row_count()):
			obj_id = self.get_item(row, 0).obj_id_row
			if obj_id is None:
				continue
			data[obj_id] = {}
			for col in range(self.get_column_count()):
				item = self.get_item(row, col)
				data[obj_id][(item.class_name, item.descriptor_name)] = item.value
		return data
		
	@QtCore.Slot(int)
	def on_tab_changed(self, index):
		
		if index == 1:
			self.populate_tab_images()
		elif index == 2:
			self.populate_tab_graph()
		
		self.update_count()
		self.get_current_tab().on_selected()
	
	@QtCore.Slot(int)
	def on_zoom(self, value):
		
		self.tab_images.set_thumbnail_size(value)
	
	@QtCore.Slot()
	def on_filter(self):
		
		self._filter_timer.start(1000)
	
	@QtCore.Slot()
	def on_filter_timer(self):
		
		self.tab_table.apply_filter(self.footer.get_filter_text())
		if isinstance(self.tab_images, QueryTabImages):
			self.tab_images.apply_filter(self.tab_table.get_item_order())
		if isinstance(self.tab_graph, QueryTabGraph):
			self.tab_graph.apply_filter()
		self.update_count()
	
	@QtCore.Slot()
	def on_sorted(self):
		
		self.tab_images.sort(self.tab_table.get_item_order())
	
	@QtCore.Slot()
	def on_add_object(self):
		
		self.signal_add_object.emit(self._query)
	
	@QtCore.Slot()
	def on_del_object(self):
		
		self.signal_del_object.emit()
	
	@QtCore.Slot()
	def on_del_descriptor(self):
		
		self.signal_del_descriptor.emit()
	
	@QtCore.Slot()
	def on_add_class(self):
		
		self.signal_add_class.emit()
	
	@QtCore.Slot()
	def on_del_class(self):
		
		self.signal_del_class.emit(self._query)
	
	@QtCore.Slot(int)
	def on_to_object(self, obj_id):
		
		if obj_id is None:
			return
		self.tabs.setCurrentIndex(0)
		self.tab_table.select_object(obj_id)
	
	@QtCore.Slot(int)
	def on_object_link(self, obj_id):
		
		self.on_to_object(obj_id)
	
	def on_query_activated(self, item):
		
		self.signal_query_activated.emit(item)
	
	def on_query_selected(self, items):
		
		self.signal_query_selected.emit(items)
		
		has_descriptor = False
		for item in items:
			if (item.obj_id is not None) and (item.value is not None):
				has_descriptor = True
				break
		found = False
		for item in items:
			if item.obj_id is not None:
				self.relation_frame.populate(self._cmodel.get_object(item.obj_id))
				found = True
				break
		if not found:
			self.relation_frame.populate()
		
		self.footer.set_del_descriptor_enabled(has_descriptor)
		self.footer.set_add_class_enabled(found)
		self.footer.set_del_class_enabled(found)
	
	def on_object_activated(self, obj_id):
		
		self.on_to_object(obj_id)
	
	def on_object_selected(self, object_ids):
		
		objects = [self._cmodel.get_object(obj_id) for obj_id in object_ids]
		obj = None
		if len(objects) == 1:
			obj = objects[0]
		self.relation_frame.populate()
		self.signal_object_selected.emit(objects)
	
	def on_relation_selected(self, relations):
		
		self.signal_relation_selected.emit([(self._cmodel.get_object(source), self._cmodel.get_object(target), label) for source, target, label in relations])
	
	def on_selected_rows(self, row_items):
		
		self.footer.set_del_object_enabled(len(row_items) > 0)
	
	def on_edited(self, item, value):
		
		self.signal_edited.emit(item, value)
	
	def on_drop_url(self, item, url):
		
		self.signal_drop_url.emit(item, url)
	
	def on_deactivate(self):
		
		self.tab_table.clearSelection()
		self.tab_images.clearSelection()
		self.tab_graph.deselect_all()
	
	def on_close(self):
		
		self._filter_timer.stop()
		self.tab_table.on_close()
		self.tab_images.on_close()
		self.tab_graph.on_close()

class QueryFooter(QtWidgets.QFrame):

	def __init__(self, queryframe):

		QtWidgets.QFrame.__init__(self)
		
		self._queryframe = queryframe
		self._count_text = None
		
		self.setFrameShape(QtWidgets.QFrame.StyledPanel)
		self.setFrameShadow(QtWidgets.QFrame.Raised)

		layout = QtWidgets.QGridLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(5, 0, 0, 0)
		self.layout().setSpacing(0)
		

		self.add_object_button = QtWidgets.QToolButton()
		self.add_object_button.setIcon(self._queryframe.get_icon("add_object.svg"))
		self.add_object_button.setIconSize(QtCore.QSize(24, 24))
		self.add_object_button.setAutoRaise(True)
		self.add_object_button.setToolTip("Add Object")
		self.add_object_button.setContentsMargins(0, 0, 0, 0)
		self.add_object_button.clicked.connect(self._queryframe.on_add_object)
		self.layout().addWidget(self.add_object_button, 0, 0)
		
		self.add_class_button = QtWidgets.QToolButton()
		self.add_class_button.setIcon(self._queryframe.get_icon("add_class.svg"))
		self.add_class_button.setIconSize(QtCore.QSize(24, 24))
		self.add_class_button.setAutoRaise(True)
		self.add_class_button.setToolTip("Add To Class")
		self.add_class_button.setContentsMargins(0, 0, 0, 0)
		self.add_class_button.clicked.connect(self._queryframe.on_add_class)
		self.layout().addWidget(self.add_class_button, 0, 1)
		
		self.del_object_button = QtWidgets.QToolButton()
		self.del_object_button.setIcon(self._queryframe.get_icon("remove_object.svg"))
		self.del_object_button.setIconSize(QtCore.QSize(24, 24))
		self.del_object_button.setAutoRaise(True)
		self.del_object_button.setToolTip("Remove Object")
		self.del_object_button.setContentsMargins(0, 0, 0, 0)
		self.del_object_button.clicked.connect(self._queryframe.on_del_object)
		self.layout().addWidget(self.del_object_button, 0, 2)
		
		self.del_descriptor_button = QtWidgets.QToolButton()
		self.del_descriptor_button.setIcon(self._queryframe.get_icon("remove_descriptor.svg"))
		self.del_descriptor_button.setIconSize(QtCore.QSize(24, 24))
		self.del_descriptor_button.setAutoRaise(True)
		self.del_descriptor_button.setToolTip("Remove Descriptor")
		self.del_descriptor_button.setContentsMargins(0, 0, 5, 0)
		self.del_descriptor_button.clicked.connect(self._queryframe.on_del_descriptor)
		self.layout().addWidget(self.del_descriptor_button, 0, 3)
		
		self.del_class_button = QtWidgets.QToolButton()
		self.del_class_button.setIcon(self._queryframe.get_icon("remove_class.svg"))
		self.del_class_button.setIconSize(QtCore.QSize(24, 24))
		self.del_class_button.setAutoRaise(True)
		self.del_class_button.setToolTip("Remove From Class")
		self.del_class_button.setContentsMargins(0, 0, 5, 0)
		self.del_class_button.clicked.connect(self._queryframe.on_del_class)
		self.layout().addWidget(self.del_class_button, 0, 4)
		
		filter_label = QtWidgets.QLabel("Filter:")
		filter_label.setContentsMargins(5, 0, 0, 0)
		self.layout().addWidget(filter_label, 0, 5)

		self._filter_edit = QtWidgets.QLineEdit()
		self._filter_edit.setContentsMargins(5, 0, 5, 0)
		self._filter_edit.textEdited.connect(self._queryframe.on_filter)
		self.layout().addWidget(self._filter_edit, 0, 6)

		self._count_label = QtWidgets.QLabel("Found: %s")
		self._count_label.setContentsMargins(0, 0, 5, 0)
		self.layout().addWidget(self._count_label, 0, 7)
		
		self._count_text = self._count_label.text()
	
	def get_filter_text(self):
		
		return self._filter_edit.text()
	
	def set_count(self, count):

		self._count_label.setText(self._count_text % (count))
	
	def set_object_buttons_enabled(self, state):

		self.add_object_button.setVisible(state)
		self.del_object_button.setVisible(state)
	
	def set_add_class_enabled(self, state):
		
		self.add_class_button.setEnabled(state)
	
	def set_del_object_enabled(self, state):
		
		self.del_object_button.setEnabled(state)
	
	def set_del_descriptor_enabled(self, state):
		
		self.del_descriptor_button.setEnabled(state)
	
	def set_del_class_enabled(self, state):
		
		self.del_class_button.setEnabled(state)

