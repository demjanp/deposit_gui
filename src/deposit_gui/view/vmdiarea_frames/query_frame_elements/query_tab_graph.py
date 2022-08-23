from deposit_gui.view.vmdiarea_frames.query_frame_elements.abstract_query_tab import AbstractQueryTab
from deposit_gui.dgui.dgraph_view import (DGraphView, Node, NodeWithAttributes, NodeWithSimpleAttributes)
from deposit.utils.fnc_files import (sanitize_filename)

from PySide2 import (QtWidgets, QtCore, QtGui)
from pathlib import Path
import os

class QueryTabGraphLazy(AbstractQueryTab, QtWidgets.QWidget):
	
	def __init__(self, queryframe):
		
		QtWidgets.QWidget.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
	
	def get_row_count(self):
		
		return len(self._query)
	
	def deselect_all(self):
		
		pass
	
class QueryTabGraph(AbstractQueryTab, QtWidgets.QMainWindow):
	
	def __init__(self, queryframe, objects):
		
		QtWidgets.QMainWindow.__init__(self)
		
		self._queryframe = queryframe
		self._query = queryframe._query
		
		self._actions = {} # {name: QAction, ...}
		self._positions = {}  # {node_id: (x, y), ...}
		self._show_attributes = 1  # 0 = show nodes only; 1 = show descriptor values; 2 = show descriptor names and values
		self._objects = objects
		
		self._graph_view = DGraphView()
		self._graph_view.signal_node_activated.connect(self.on_activated)
		self._graph_view.signal_selected.connect(self.on_graph_selected)
		
		central_widget = QtWidgets.QWidget(self)
		central_widget.setLayout(QtWidgets.QVBoxLayout())
		central_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(central_widget)
		central_widget.layout().addWidget(self._graph_view)
		
		self.toolbar = self.addToolBar("Graph")
		actions = [
			["node_view", "Show Nodes", "nodes.svg"],
			["value_view", "Show Values", "attributes_simple.svg"],
			["descriptor_view", "Show Descriptors with Values", "attributes.svg"],
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
				self._actions[name] = QtWidgets.QAction(self._queryframe.get_icon(icon), text, self)
				self._actions[name].setData(name)
				self.toolbar.addAction(self._actions[name])
		
		self._actions["node_view"].setCheckable(True)
		self._actions["value_view"].setCheckable(True)
		self._actions["descriptor_view"].setCheckable(True)
		self._actions["node_view"].setChecked(False)
		self._actions["value_view"].setChecked(True)
		self._actions["descriptor_view"].setChecked(False)
		
		self.toolbar.actionTriggered.connect(self.on_tool_triggered)
		
		self.populate_graph()
	
	def update_query(self):
		
		self.populate_graph()
	
	def populate_graph(self):
		
		self._graph_view.clear()
		
		if self._objects is None:
			return
		
		self._queryframe._cview.progress.show("Drawing Tree")
		
		nodes = []  # [AbstractNode, ...]
		edges = []  # [[source_id, target_id, label], ...]
		for obj in self._objects:
			
			descriptors = []
			if self._show_attributes > 0:
				for descr in obj.get_descriptors():
					value = obj.get_descriptor(descr)
					if value.__class__.__name__ == "DDateTime":
						value = value.isoformat
					elif value.__class__.__name__ == "DGeometry":
						value = value.geometry_type
					elif value.__class__.__name__ == "DResource":
						value = value.filename
					else:
						value = str(value)
					descriptors.append([descr.name, value])
			
			if self._show_attributes == 0:
				nodes.append(Node(obj.id, str(obj.id)))
			elif self._show_attributes == 1:
				nodes.append(NodeWithSimpleAttributes(obj.id, str(obj.id), descriptors))
			elif self._show_attributes == 2:
				nodes.append(NodeWithAttributes(obj.id, str(obj.id), descriptors))
			
			for obj_tgt, label in obj.get_relations():
				if label.startswith("~"):
					continue
				if obj_tgt in self._objects:
					edges.append([obj.id, obj_tgt.id, label])
		
		self._graph_view.populate(nodes = nodes, edges = edges, positions = self._positions, progress = self._queryframe._cview.progress)
		
		self._queryframe._cview.progress.stop()
	
	def apply_filter(self, objects):
		
		self._objects = objects
		if self.isVisible():
			self.populate_graph()
	
	def show(self):
		
		QtWidgets.QMainWindow.show(self)
		
		self.populate_graph()
	
	def get_row_count(self):
		
		return len(self._query)
	
	def deselect_all(self):
		
		self._graph_view.deselect_all()
	
	@QtCore.Slot(object)
	def on_tool_triggered(self, action):
		
		fnc_name = "on_%s" % str(action.data())
		if hasattr(self, fnc_name):
			getattr(self, fnc_name)()
	
	@QtCore.Slot(object)
	def on_activated(self, obj_id):
		
		self._queryframe.on_object_activated(obj_id)
	
	@QtCore.Slot()
	def on_graph_selected(self):
		
		self.on_selected()
	
	def on_selected(self):
		
		nodes, edges = self._graph_view.get_selected()
		self._queryframe.on_object_selected(nodes)
		if nodes:
			return
		self._queryframe.on_relation_selected(edges)
		
	
	# Toolbar actions
	
	def on_node_view(self):
		
		self.update_view(0)
	
	def on_value_view(self):
		
		self.update_view(1)
	
	def on_descriptor_view(self):
		
		self.update_view(2)
	
	def update_view(self, show_attributes):
		
		self._show_attributes = show_attributes
		for n, name in [(0, "node_view"), (1, "value_view"), (2, "descriptor_view")]:
			self._actions[name].blockSignals(True)
			self._actions[name].setChecked(show_attributes == n)
			self._actions[name].blockSignals(False)
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
		
		name = None
		if self._query.main_class is not None:
			name = self._query.main_class.strip(".")
		filename = sanitize_filename(name + ".pdf", default = "objects.pdf")
		
		recent_dir = self._queryframe._cview.get_recent_dir()
		if not recent_dir:
			recent_dir = str(Path.home())
		path = os.path.join(recent_dir, filename)
		path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save As Adobe PDF", path, "Adobe PDF (*.pdf)")
		if not path:
			return
		self._graph_view.save_pdf(path)
		self._queryframe._cview.set_recent_dir(os.path.dirname(path))

