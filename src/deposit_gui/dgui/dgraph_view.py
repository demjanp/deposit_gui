from deposit_gui.dgui import pygraphviz

from PySide2 import (QtWidgets, QtCore, QtGui, QtPrintSupport)
from collections import defaultdict
import networkx as nx
import weakref
import math

def to_agraph(N):
	
	directed = N.is_directed()
	strict = nx.number_of_selfloops(N) == 0 and not N.is_multigraph()
	A = pygraphviz.AGraph(name=N.name, strict=strict, directed=directed)

	# default graph attributes
	A.graph_attr.update(N.graph.get("graph", {}))
	A.node_attr.update(N.graph.get("node", {}))
	A.edge_attr.update(N.graph.get("edge", {}))

	A.graph_attr.update(
		(k, v) for k, v in N.graph.items() if k not in ("graph", "node", "edge")
	)

	# add nodes
	for n, nodedata in N.nodes(data=True):
		A.add_node(n)
		# Add node data
		a = A.get_node(n)
		a.attr.update({k: str(v) for k, v in nodedata.items()})

	# loop over edges
	if N.is_multigraph():
		for u, v, key, edgedata in N.edges(data=True, keys=True):
			str_edgedata = {k: str(v) for k, v in edgedata.items() if k != "key"}
			A.add_edge(u, v, key=str(key))
			# Add edge data
			a = A.get_edge(u, v)
			a.attr.update(str_edgedata)

	else:
		for u, v, edgedata in N.edges(data=True):
			str_edgedata = {k: str(v) for k, v in edgedata.items()}
			A.add_edge(u, v)
			# Add edge data
			a = A.get_edge(u, v)
			a.attr.update(str_edgedata)

	return A

def pygraphviz_layout(G, prog="dot", root=None, args=""):
	
	if root is not None:
		args += f"-Groot={root}"
	A = to_agraph(G)
	A.layout(prog=prog, args=args)
	node_pos = {}
	for n in G:
		node = pygraphviz.Node(A, n)
		try:
			xs = node.attr["pos"].split(",")
			node_pos[n] = tuple(float(x) for x in xs)
		except:
			print("no position for node", n)
			node_pos[n] = (0.0, 0.0)
	return node_pos


NODE_TYPE = QtWidgets.QGraphicsItem.UserType + 1
EDGE_TYPE = QtWidgets.QGraphicsItem.UserType + 2

class AbstractNode(QtWidgets.QGraphicsItem):
	
	type = NODE_TYPE
	
	def __init__(self, node_id, label = "", font_family = "Calibri", font_size = 16):
		
		self.node_id = node_id
		self.label = str(label)
		self.edges = []  # [Edge, ...]
		self.font = QtGui.QFont(font_family, font_size)
		self.label_w = 0
		self.label_h = 0
		
		QtWidgets.QGraphicsItem.__init__(self)
		
		if self.label != "":
			rect = QtGui.QFontMetrics(self.font).boundingRect(self.label)
			self.label_w = rect.width()
		
		self.setAcceptHoverEvents(True)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
		self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
		self.setCacheMode(self.DeviceCoordinateCache)
		self.setZValue(-1)
	
	def add_edge(self, edge):
		
		self.edges.append(weakref.ref(edge))
		edge.adjust()
	
	def center(self):
		
		return self.boundingRect().center()
	
	def shape(self):
		
		return QtGui.QPainterPath()
	
	def on_hover(self, state):
		# state: True = Enter, False = Leave
		# re-implement
		
		pass
	
	def on_position_change(self):
		# re-implement
		
		pass
	
	def on_mouse_press(self):
		# re-implement
		
		pass
	
	def on_mouse_release(self):
		# re-implement
		
		pass
	
	def hoverEnterEvent(self, event):
		
		self.on_hover(True)
		
		QtWidgets.QGraphicsItem.hoverEnterEvent(self, event)
	
	def hoverLeaveEvent(self, event):
		
		self.on_hover(False)
		
		QtWidgets.QGraphicsItem.hoverLeaveEvent(self, event)
	
	def itemChange(self, change, value):
		
		if change == QtWidgets.QGraphicsItem.ItemPositionChange:
			for edge in self.edges:
				edge().adjust()
			
			self.on_position_change()
		
		return QtWidgets.QGraphicsItem.itemChange(self, change, value)
	
	def mousePressEvent(self, event):
		
		self.update()
		self.on_mouse_press()
		QtWidgets.QGraphicsItem.mousePressEvent(self, event)
	
	def mouseReleaseEvent(self, event):
		
		self.update()
		self.on_mouse_release()
		QtWidgets.QGraphicsItem.mouseReleaseEvent(self, event)

class Node(AbstractNode):
	
	def __init__(self, node_id, label = "", radius = 10, font_family = "Calibri", font_size = 16):
		
		AbstractNode.__init__(self, node_id, label, font_family, font_size)
		
		self.radius = radius
	
	def boundingRect(self):
		
		adjust = 2		
		return QtCore.QRectF(-self.radius - adjust, -self.radius - adjust, (2*self.radius) + 3 + adjust, (2*self.radius) + 3 + adjust)
	
	def center(self):
		
		return QtCore.QPointF(0, 0)
	
	def shape(self):
		
		path = QtGui.QPainterPath()
		path.addEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
		return path
	
	def paint(self, painter, option, widget):
		
		pen_width = 0
		if option.state & QtWidgets.QStyle.State_Sunken:
			pen_width = 2
		if option.state & QtWidgets.QStyle.State_Selected:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
		else:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
		painter.setPen(QtGui.QPen(QtCore.Qt.black, pen_width))
		painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
		if self.label != "":
			painter.setFont(self.font)
			painter.drawText(25, 8, self.label)
	
	def on_hover(self, state):
		# state: True = Enter, False = Leave
		# re-implement
		
		pass
	
	def on_position_change(self):
		# re-implement
		
		pass
	
	def on_mouse_press(self):
		# re-implement
		
		pass
	
	def on_mouse_release(self):
		# re-implement
		
		pass
	
class NodeWithAttributes(AbstractNode):
	
	def __init__(self, node_id, label = "", descriptors = [], font_family = "Calibri", font_size = 14, max_width = 256):
		# descriptors = [(name, value), ...]
		
		AbstractNode.__init__(self, node_id, label, font_family, font_size)
		
		self.descriptors = []
		self.descriptor_w = 0
		self.descriptor_h = 0
		self.selection_polygon = None
		self.selection_shape = None
		self.text_padding = 3
		self.max_width = max_width
		
		self.populate_descriptors(descriptors)
		self.adjust()
	
	def populate_descriptors(self, descriptors):
		
		for name, value in descriptors:
			if value:
				self.descriptors.append("%s: %s" % (name, value))
			else:
				self.descriptors.append(name)
	
	def adjust(self):
		
		adjust_w = 2
		adjust_h = 0
		
		if self.label != "":
			rect = QtGui.QFontMetrics(self.font).boundingRect(self.label)
			self.label_w = rect.width() + adjust_w
			self.label_h = rect.height() + adjust_h
		
		self.descriptor_w = 0
		self.descriptor_h = 0
		for text in self.descriptors:
			rect = QtGui.QFontMetrics(self.font).boundingRect(text)
			self.descriptor_w = max(self.descriptor_w, rect.width() + adjust_w)
			self.descriptor_h = max(self.descriptor_h, rect.height() + adjust_h)
		
		self.descriptor_w = min(self.descriptor_w, self.max_width)
		
		w = max(self.label_w, self.descriptor_w) + 2*self.text_padding
		h = self.label_h + 2*self.text_padding + len(self.descriptors)*(self.descriptor_h + self.text_padding) + self.text_padding
		
		self.selection_polygon = QtGui.QPolygonF(QtCore.QRectF(0, 0, w, h))
		self.selection_shape = QtGui.QPainterPath()
		self.selection_shape.addPolygon(self.selection_polygon)
	
	def boundingRect(self):
		
		return self.selection_polygon.boundingRect()
	
	def center(self):
		
		return self.boundingRect().center()
	
	def shape(self):
		
		return self.selection_shape
	
	def paint(self, painter, option, widget):
		
		adjust_y = -2
		
		pen_width = 0
		if option.state & QtWidgets.QStyle.State_Sunken:
			pen_width = 2
		
		y = self.label_h + 2*self.text_padding + adjust_y
		rect = self.selection_polygon.boundingRect()
		
		painter.setPen(QtCore.Qt.NoPen)
		painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
		painter.drawPath(self.selection_shape)
		
		painter.setPen(QtCore.Qt.NoPen)
		if option.state & QtWidgets.QStyle.State_Selected:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.darkGray))
		else:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
		painter.drawRect(0, 0, rect.width(), y)
		
		painter.setPen(QtGui.QPen(QtCore.Qt.black, pen_width))
		painter.setBrush(QtCore.Qt.NoBrush)
		painter.drawLine(0, y, rect.width(), y)
		painter.drawPath(self.selection_shape)
		
		painter.setFont(self.font)
		
		if self.label != "":
			painter.drawText(self.text_padding, self.label_h + adjust_y, self.label)
		
		for n, text in enumerate(self.descriptors):
			painter.drawText(self.text_padding, y + (n + 1)*(self.descriptor_h + self.text_padding) + adjust_y, text)
	
	def on_hover(self, state):
		# state: True = Enter, False = Leave
		# re-implement
		
		pass
	
	def on_position_change(self):
		# re-implement
		
		pass
	
	def on_mouse_press(self):
		# re-implement
		
		pass
	
	def on_mouse_release(self):
		# re-implement
		
		pass

class NodeWithSimpleAttributes(NodeWithAttributes):
	
	def populate_descriptors(self, descriptors):
		
		for _, value in descriptors:
			self.descriptors.append(str(value))
	
	def adjust(self):
		
		adjust_w = 2
		adjust_h = 0
		
		self.descriptor_w = 0
		self.descriptor_h = 0
		for text in self.descriptors:
			rect = QtGui.QFontMetrics(self.font).boundingRect(text)
			self.descriptor_w = max(self.descriptor_w, rect.width() + adjust_w)
			self.descriptor_h = max(self.descriptor_h, rect.height() + adjust_h)
		
		self.descriptor_w = min(self.descriptor_w, self.max_width)
		
		w = self.descriptor_w + 2*self.text_padding
		h = len(self.descriptors)*(self.descriptor_h + self.text_padding) + self.text_padding
		
		self.selection_polygon = QtGui.QPolygonF(QtCore.QRectF(0, 0, w, h))
		self.selection_shape = QtGui.QPainterPath()
		self.selection_shape.addPolygon(self.selection_polygon)
	
	def paint(self, painter, option, widget):
		
		adjust_y = -2
		
		pen_width = 0
		if option.state & QtWidgets.QStyle.State_Sunken:
			pen_width = 2
		
		painter.setPen(QtCore.Qt.NoPen)
		if option.state & QtWidgets.QStyle.State_Selected:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
		else:
			painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
		
		painter.setPen(QtGui.QPen(QtCore.Qt.black, pen_width))
		
		painter.drawPath(self.selection_shape)
		
		y = adjust_y
		
		painter.setFont(self.font)
		
		for n, text in enumerate(self.descriptors):
			painter.drawText(self.text_padding, y + (n + 1)*(self.descriptor_h + self.text_padding) + adjust_y, text)
	
	def on_hover(self, state):
		# state: True = Enter, False = Leave
		# re-implement
		
		pass
	
	def on_position_change(self):
		# re-implement
		
		pass
	
	def on_mouse_press(self):
		# re-implement
		
		pass
	
	def on_mouse_release(self):
		# re-implement
		
		pass

class Edge(QtWidgets.QGraphicsItem):
	
	type = EDGE_TYPE
	
	def __init__(self, source, target, label = "", color = None, offset = 0, font_family = "Calibri", font_size = 16, arrow_size = 20):
		# offset = display edge as curve with highest point offset by this distance from a line
		
		QtWidgets.QGraphicsItem.__init__(self)
		
		self.label = label
		self.color = QtCore.Qt.gray if color is None else color
		self.source = weakref.ref(source)
		self.target = weakref.ref(target)
		self.offset = offset
		self.is_loop = (source.node_id == target.node_id)
		self.arrow_size = arrow_size
		self.font = QtGui.QFont(font_family, font_size)
		self.label_w = 0
		self.label_h = 0
		self.line = None
		self.edge_path = QtGui.QPainterPath()
		self.selection_shape = QtGui.QPainterPath()
		
		if self.label != "":
			rect = QtGui.QFontMetrics(self.font).boundingRect(self.label)
			self.label_w = rect.width()
			self.label_h = rect.height()
		
		if isinstance(self.color, str):
			self.color = getattr(QtCore.Qt, self.color)
		
		self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)
		self.setCacheMode(self.DeviceCoordinateCache)
		self.setZValue(-2)
		
		self.source().add_edge(self)
		self.target().add_edge(self)
		self.adjust()
	
	def get_angle(self):
		
		if self.is_loop:
			return 45
		length = self.line.length()
		if length:
			angle = math.acos(self.line.dx() / length)
		else:
			angle = 0
		if self.line.dy() >= 0:
			angle = 2*math.pi - angle
		return angle
	
	def adjust(self):
		
		self.edge_path = QtGui.QPainterPath()
		self.selection_shape = QtGui.QPainterPath()
		
		if not self.source() or not self.target():
			return
		
		self.line = QtCore.QLineF(self.mapFromItem(self.source(), self.source().center()), self.mapFromItem(self.target(), self.target().center()))
		
		self.prepareGeometryChange()
		
		selection_offset = 7
		
		if self.is_loop:
			d = self.arrow_size * 3
			x, y = self.line.p1().x() - d, self.line.p1().y() - d
			self.edge_path.arcMoveTo(x, y, d, d, 270)
			self.edge_path.arcTo(x, y, d, d, 270, 360)
			self.selection_shape = QtGui.QPainterPath(self.edge_path)
			
		else:
			angle = self.get_angle()
			self.edge_path.moveTo(self.line.p1())
			offset = ((self.offset + 1) // 2)
			step = max(10, self.arrow_size*2.5, self.label_h*2)
			offset *= step
			if self.offset % 2 == 1:
				offset *= -1
			controlpoint = self.line.center() + QtCore.QPointF(math.sin(angle - math.pi) * offset, math.cos(angle - math.pi) * offset)
			self.edge_path.quadTo(controlpoint, self.line.p2())
			
			rad_angle = self.line.angle() * math.pi / 180
			dx = selection_offset * math.sin(rad_angle)
			dy = selection_offset * math.cos(rad_angle)
			path = QtGui.QPainterPath(self.edge_path)
			path.translate(dx, dy)
			self.selection_shape.connectPath(path)
			path = QtGui.QPainterPath(self.edge_path.toReversed())
			path.translate(-dx, -dy)
			self.selection_shape.connectPath(path)
	
	def boundingRect(self):
		
		rect = self.selection_shape.boundingRect()
		x0, y0, w, h = rect.x(), rect.y(), rect.width(), rect.height()
		x1, y1 = x0 + w, y0 + h
		if self.is_loop:
			x0 -= self.arrow_size
		if self.label != "":
			text_pos = self.edge_path.pointAtPercent(0.5)
			x0 = min(x0, text_pos.x() - self.label_w / 2 - 4)
			y0 = min(y0, text_pos.y() - self.label_h / 2 - 4)
			x1 = max(x1, text_pos.x() + self.label_w / 2)
			y1 = max(y1, text_pos.y() + self.label_h / 2)
		return QtCore.QRectF(x0, y0, x1 - x0, y1 - y0)
	
	def shape(self):
		
		return self.selection_shape
	
	def paint(self, painter, option, widget):
		
		if not self.source() or not self.target():
			return
		
		pen_width = 1
		if option.state & QtWidgets.QStyle.State_Selected:
			pen_width = 2
		
		pen = QtGui.QPen(self.color, pen_width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
		pen.setCosmetic(True)
		
		painter.setPen(pen)
		
		angle = self.get_angle()
		
		painter.strokePath(self.edge_path, pen)
		
		if self.arrow_size > 0:
			arrow_pos = self.edge_path.pointAtPercent(0.6)
			arrow_p1 = arrow_pos + QtCore.QPointF(math.sin(angle - math.pi / 3) * self.arrow_size, math.cos(angle - math.pi / 3) * self.arrow_size)
			arrow_p2 = arrow_pos + QtCore.QPointF(math.sin(angle - math.pi + math.pi / 3) * self.arrow_size, math.cos(angle - math.pi + math.pi / 3) * self.arrow_size)
			painter.setBrush(self.color)
			painter.drawPolygon(QtGui.QPolygonF([arrow_pos, arrow_p1, arrow_p2]))
		
		if self.label != "":
			painter.setFont(self.font)
			painter.setPen(QtGui.QPen(QtCore.Qt.black, pen_width))
			text_pos = self.edge_path.pointAtPercent(0.5)
			x = text_pos.x()
			y = text_pos.y()
			painter.drawText(x - self.label_w / 2, y + self.label_h / 4, self.label)

class DGraphView(QtWidgets.QGraphicsView):
	
	signal_node_activated = QtCore.Signal(object)
	signal_selected = QtCore.Signal()
	
	def __init__(self):
		
		self._nodes = {}  # {node_id: Node, ...}
		self._edges = []  # [Edge, ...]
		self._mouse_prev = None
		self._edge_font_family = 16
		self._edge_font_size = 16
		
		QtWidgets.QGraphicsView.__init__(self)
		
		scene = QtWidgets.QGraphicsScene(self)
		scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
		self.setScene(scene)
		self.setRenderHint(QtGui.QPainter.Antialiasing)
		self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
		self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
		
		self.setMinimumSize(200, 200)
		
		scene.selectionChanged.connect(self.on_selected)
	
	def clear(self):
		
		self.scene().clear()
		self.setSceneRect(QtCore.QRectF())
		self._nodes.clear()
		self._edges.clear()
	
	def reset_scene(self):
		
		rect = self.scene().itemsBoundingRect().marginsAdded(QtCore.QMarginsF(10, 10, 10, 10))
		self.setSceneRect(rect)
		self.fitInView(rect, QtCore.Qt.KeepAspectRatio)
	
	def calc_positions(self, nodes, edges, gap = 10, x_stretch = 1, y_stretch = 1, move_nodes = None):
		# nodes = [AbstractNode, node_id, ...]
		# edges = [[source_id, target_id], ...]
		# move_nodes = [node_id, ...]; if set, only calculate positions for those nodes
		#
		# returns {node_id: (x, y), ...}
		
		pos_collect = {}
		done = set([])
		y_max = 0
		if move_nodes is not None:
			done = set(move_nodes)
		G = nx.DiGraph()
		for row in edges:
			source_id, target_id = row[:2]
			if move_nodes is not None:
				if (source_id not in move_nodes) or (target_id not in move_nodes):
					continue
			G.add_edge(source_id, target_id)
			if move_nodes is None:
				done.add(source_id)
				done.add(target_id)
		for node_id in nodes:
			if isinstance(node_id, AbstractNode):
				node_id = node_id.node_id
			if (move_nodes is not None) and (node_id not in move_nodes):
				continue
			G.add_node(node_id)
			if move_nodes is None:
				done.add(node_id)
		for node_id in done:
			rect = self._nodes[node_id].boundingRect()
			mul = 0.013  # TODO find a way to calculate
			w, h = rect.width(), rect.height()
			G.nodes[node_id]["width"] = (w + 2*gap) * mul
			G.nodes[node_id]["height"] = (h + 2*gap) * mul
		
		g_positions = pygraphviz_layout(G, prog = "dot")
		
		for node_id in g_positions:
			x, y = g_positions[node_id]
			g_positions[node_id] = (x * x_stretch, y * y_stretch)
		xmin, ymax = math.inf, -math.inf
		for node_id in g_positions:
			x, y = g_positions[node_id]
			xmin = min(xmin, x)
			ymax = max(ymax, y)
		for node_id in g_positions:
			x, y = g_positions[node_id]
			g_positions[node_id] = (x - xmin, ymax - y)
		
		for node_id in g_positions:
			pos_collect[node_id] = tuple(g_positions[node_id])
			y_max = max(y_max, pos_collect[node_id][1])
		
		n = len([node_id for node_id in self._nodes if node_id not in done])
		if n > 3:
			n_side = max(1, int(n**0.5))
		else:
			n_side = n
		
		x = 0
		y = y_max
		h_max = 0
		n = 0
		for node_id in self._nodes:
			if node_id in done:
				continue
			pos_collect[node_id] = (x, y)
			rect = self._nodes[node_id].boundingRect()
			w, h = rect.width() + gap, rect.height() + gap
			h_max = max(h_max, h)
			x += w
			n += 1
			if n > n_side:
				x = 0
				y += h_max
				h_max = 0
				n = 0
		
		return pos_collect
	
	def populate(self, nodes = [], edges = [], positions = {}, gap = 10, x_stretch = 1, y_stretch = 1, edge_font_family = "Calibri", edge_font_size = 16, edge_arrow_size = 20, move_nodes = None, progress = None):
		# nodes = [AbstractNode, (node_id, label), ...]
		# edges = [[source_id, target_id], [source_id, target_id, label], [source_id, target_id, label, color], ...]
		# positions = {node_id: (x, y), ...}
		# move_nodes = [node_id, ...]; if set, only calculate positions for those nodes
		
		self.clear()
		
		self.hide()
		
		for node in nodes:
			if isinstance(node, tuple):
				node_id, label = node
				node = Node(node_id, label)
			self._nodes[node.node_id] = node
		
		node_ids = move_nodes
		if node_ids is None:
			node_ids = list(self._nodes.keys())
		if False in [(node_id in positions) for node_id in node_ids]:
			positions_new = self.calc_positions(self._nodes, edges, gap, x_stretch, y_stretch, move_nodes)
			positions_new.update(positions)
			positions.clear()
			positions.update(positions_new)
		
		cnt = 0
		cmax = len(self._nodes) + len(edges)
		for node_id in self._nodes:
			cnt += 1
			if progress is not None:
				progress.update_state(text = "Drawing Tree", value = cnt, maximum = cmax)
				if progress.cancel_pressed():
					self.clear()
					self.show()
					return
			
			self._nodes[node_id].setPos(*positions[node_id])
			self.scene().addItem(self._nodes[node_id])
		
		edges_done = defaultdict(int)
		for row in edges:
			cnt += 1
			if progress is not None:
				progress.update_state(text = "Drawing Tree", value = cnt, maximum = cmax)
				if progress.cancel_pressed():
					self.clear()
					self.show()
					return
			attrs = [None, None, "", "black"]
			attrs[:len(row)] = row
			source_id, target_id, label, color = attrs
			if (source_id not in self._nodes) or (target_id not in self._nodes):
				continue
			key = tuple(sorted([source_id, target_id]))
			self._edges.append(Edge(self._nodes[source_id], self._nodes[target_id], label, color, offset = edges_done[key], font_family = edge_font_family, font_size = edge_font_size, arrow_size = edge_arrow_size))
			edges_done[key] += 1
			self.scene().addItem(self._edges[-1])
		
		self.reset_scene()
		self.show()
	
	def get_node(self, node_id):
		
		if node_id in self._nodes:
			return self._nodes[node_id]
		return None
	
	def get_nodes(self):
		
		return self._nodes
	
	def get_edges(self):
		
		return self._edges
	
	def get_selected(self):
		
		nodes = []
		edges = []
		for item in self.scene().selectedItems():
			if item.type == NODE_TYPE:
				nodes.append(item.node_id)
			elif item.type == EDGE_TYPE:
				edges.append((item.source().node_id, item.target().node_id, item.label))
		return nodes, edges
	
	def get_positions(self):
		
		positions = {}
		for node_id in self._nodes:
			pos = self._nodes[node_id].pos()
			x, y = pos.x(), pos.y()
			positions[node_id] = (x, y)
		return positions
	
	def get_scale(self):
		
		return self.transform().m11()
	
	def select_node(self, node_id):
		
		if node_id in self._nodes:
			self._nodes[node_id].setSelected(True)
	
	def deselect_all(self):
		
		self.scene().clearSelection()
	
	def scale_view(self, factor):
		
		self.scale(factor, factor)
	
	def save_pdf(self, path, dpi = 72):
		
		self.scene().clearSelection()
		
		scale = self.get_scale()
		
		rect = self.scene().itemsBoundingRect()
		m = min(rect.width(), rect.height())*0.05
		rect = rect.marginsAdded(QtCore.QMarginsF(m, m, m, m))
		w, h = rect.width(), rect.height()
		
		printer = QtPrintSupport.QPrinter()
		printer.setWinPageSize(QtGui.QPageSize.A4)
		printer.setFullPage(True)
		is_landscape = False
		if w > h:
			is_landscape = True
			printer.setOrientation(QtPrintSupport.QPrinter.Landscape)
		else:
			printer.setOrientation(QtPrintSupport.QPrinter.Portrait)
		printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
		printer.setOutputFileName(path)
		size = printer.pageLayout().pageSize().sizePoints()
		if is_landscape:
			pw, ph = size.height(), size.width()
		else:
			pw, ph = size.width(), size.height()
		scale = min(pw / w, ph / h)
		printer.setResolution(int(round(dpi / scale)))
		ph = int(round(h * (pw / w)))
		if is_landscape:
			printer.setPageSize(QtGui.QPageSize(QtCore.QSize(ph, pw), units = QtGui.QPageSize.Point))
		else:
			printer.setPageSize(QtGui.QPageSize(QtCore.QSize(pw, ph), units = QtGui.QPageSize.Point))
		
		painter = QtGui.QPainter(printer)
		self.scene().render(painter, source = rect)
		painter.end()
	
	@QtCore.Slot()
	def on_selected(self):
		
		self.signal_selected.emit()
	
	def wheelEvent(self, event):
		
		self.scale_view(2**(event.delta() / 240.0))
	
	def mousePressEvent(self, event):
		
		if event.button() == QtCore.Qt.LeftButton:
			self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
			self.setCursor(QtCore.Qt.ArrowCursor)
		elif event.button() == QtCore.Qt.RightButton:
			self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
			self.setCursor(QtCore.Qt.OpenHandCursor)
			self._mouse_prev = (event.x(), event.y())
		
		QtWidgets.QGraphicsView.mousePressEvent(self, event)
	
	def mouseMoveEvent(self, event):
		
		if self._mouse_prev is not None:
			prev_point = self.mapToScene(*self._mouse_prev)
			new_point = self.mapToScene(event.pos())
			translation = new_point - prev_point
			self.translate(translation.x(), translation.y())
			self._mouse_prev = (event.x(), event.y())
		
		QtWidgets.QGraphicsView.mouseMoveEvent(self, event)
	
	def mouseReleaseEvent(self, event):
		
		self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
		self.setCursor(QtCore.Qt.ArrowCursor)
		self._mouse_prev = None
		
		QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
	
	def mouseDoubleClickEvent(self, event):
		
		item = self.itemAt(event.pos())
		if item is None:
			return
		if item.type == NODE_TYPE:
			self.signal_node_activated.emit(item.node_id)

