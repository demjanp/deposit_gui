from deposit_gui.view.vmdiarea_frames.abstract_mdiarea_frame import AbstractMDIAreaFrame
from deposit_gui.dgui.dgraph_view import (DGraphView, NodeWithAttributes, NodeWithSimpleAttributes)

from PySide6 import (QtWidgets, QtCore, QtGui)
from pathlib import Path
import os

class ClassGraphFrame(AbstractMDIAreaFrame, QtWidgets.QFrame):
	
	signal_class_selected = QtCore.Signal(list)		# [Class, ...]
	signal_relation_selected = QtCore.Signal(list)		# [(Source, Target, label), ...]
	signal_activated = QtCore.Signal(object)	# Class
	
	def __init__(self, cmodel, cview):
		
		AbstractMDIAreaFrame.__init__(self)
		QtWidgets.QFrame.__init__(self)
		
		self._graph = ClassGraph(self, cmodel, cview)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		self.layout().addWidget(self._graph)
	
	def title(self):
		
		return "Class Relations"
	
	def icon(self):
		# re-implement
		
		return "classes_graph.svg"
	
	def update_classes(self):
		
		self._graph.update_classes()
	
	def on_deactivate(self):
		
		self._graph._graph_view.deselect_all()

class ClassGraph(QtWidgets.QMainWindow):
	
	def __init__(self, frame, cmodel, cview):
		
		QtWidgets.QMainWindow.__init__(self)
		
		self._frame = frame
		self._cmodel = cmodel
		self._cview = cview
		
		self._actions = {} # {name: QAction, ...}
		self._positions = {}  # {node_id: (x, y), ...}
		self._show_descriptors = False
		
		self._graph_view = DGraphView()
		self._graph_view.signal_node_activated.connect(self.on_activated)
		self._graph_view.signal_selected.connect(self.on_selected)
		
		central_widget = QtWidgets.QWidget(self)
		layout = QtWidgets.QVBoxLayout()
		central_widget.setLayout(layout)
		central_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(central_widget)
		central_widget.layout().addWidget(self._graph_view)
		
		self.toolbar = self.addToolBar("Graph")
		actions = [
			["descriptor_view", "Show Descriptors", "attributes.svg"],
			["reset_layout", "Re-arrange Layout", "geometry.svg"],
			["#separator", None, None],
			["zoom_in", "Zoom In", "zoom_in.svg"],
			["zoom_out", "Zoom Out", "zoom_out.svg"],
			["zoom_reset", "Zoom Reset", "zoom_reset.svg"],
			["#separator", None, None],
			["save_pdf", "Save As PDF", "save_pdf.svg"],
		]
		
		for name, text, icon in actions:
			if name == "#separator":
				self.toolbar.addSeparator()
			else:
				self._actions[name] = QtGui.QAction(self._frame.get_icon(icon), text, self)
				self._actions[name].setData(name)
				self.toolbar.addAction(self._actions[name])
		
		self._actions["descriptor_view"].setCheckable(True)
		
		self.toolbar.actionTriggered.connect(self.on_tool_triggered)
		
		self.populate_graph()
	
	def update_classes(self):
		
		self.populate_graph()
	
	def populate_graph(self):
		
		nodes = []
		edges = []
		descriptors = self._cmodel.get_descriptor_names()
		for cls in self._cmodel.get_classes():
			if cls.name in descriptors:
				continue
			if self._show_descriptors:
				descriptors = []
				for name in cls.get_descriptor_names(ordered = True):
					descriptors.append((name, ""))
				nodes.append(NodeWithAttributes(cls.name, cls.name, descriptors))
			else:
				nodes.append(NodeWithSimpleAttributes(cls.name, cls.name, [("name", cls.name)]))
			for cls2, label in cls.get_object_relations(direct_only = True):
				if label.startswith("~"):
					continue
				if cls2 == cls:
					continue
				edges.append([cls.name, cls2.name, label, "darkGray"])
			for cls2, label in cls.get_relations():
				if label.startswith("~"):
					continue
				if cls2 == cls:
					continue
				edge = [cls.name, cls2.name, label, "darkGray"]
				if edge not in edges:
					edges.append(edge)
		self._graph_view.populate(nodes = nodes, edges = edges, positions = self._positions)
	
	@QtCore.Slot(object)
	def on_tool_triggered(self, action):
		
		fnc_name = "on_%s" % str(action.data())
		if hasattr(self, fnc_name):
			getattr(self, fnc_name)()
	
	@QtCore.Slot(object)
	def on_activated(self, name):
		
		self._frame.signal_activated.emit(self._cmodel.get_class(name))
	
	@QtCore.Slot()
	def on_selected(self):
		
		nodes, edges = self._graph_view.get_selected()
		self._frame.signal_class_selected.emit([self._cmodel.get_class(name) for name in nodes])
		if nodes:
			return
		relations = []
		for source, target, label in edges:
			relations.append((self._cmodel.get_class(source), self._cmodel.get_class(target), label))
		self._frame.signal_relation_selected.emit(relations)
	
	
	# Toolbar actions
	
	def on_descriptor_view(self):
		
		self._show_descriptors = self._actions["descriptor_view"].isChecked()
		self.populate_graph()
	
	def on_reset_layout(self):
		
		self._positions = {}
		self.populate_graph()
	
	def on_zoom_in(self):
		
		self._graph_view.scale(1.1, 1.1)
	
	def on_zoom_out(self):
		
		self._graph_view.scale(0.9, 0.9)
	
	def on_zoom_reset(self):
		
		self._graph_view.reset_zoom()
	
	def on_save_pdf(self):
		
		filename = "%s_schema.pdf" % (self._cmodel.get_datasource_name())
		recent_dir = self._cview.get_recent_dir()
		if not recent_dir:
			recent_dir = str(Path.home())
		path = os.path.join(recent_dir, filename)
		path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save As Adobe PDF", path, "Adobe PDF (*.pdf)")
		if not path:
			return
		self._graph_view.save_pdf(path)
		self._cview.set_recent_dir(os.path.dirname(path))


