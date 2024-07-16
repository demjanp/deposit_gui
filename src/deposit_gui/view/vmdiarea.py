from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.view.vmdiarea_frames.query_frame import QueryFrame
from deposit_gui.view.vmdiarea_frames.external_frame import ExternalFrame
from deposit_gui.view.vmdiarea_frames.class_graph_frame import ClassGraphFrame

from PySide6 import (QtWidgets, QtCore, QtGui)

class VMDIArea(AbstractSubview, QtWidgets.QFrame):
	
	signal_window_activated = QtCore.Signal(bool)
	
	def __init__(self, on_drag_enter, on_drag_move, on_drop):
		
		AbstractSubview.__init__(self)
		QtWidgets.QFrame.__init__(self)
		
		self._outside_frames = []
		self._mdiarea = MDIArea(on_drag_enter, on_drag_move, on_drop)
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self._mdiarea.subWindowActivated.connect(self.on_window_activated)
		
		self.layout().addWidget(self._mdiarea)
	
	def _add_frame(self, frame):
		# frame = AbstractMDIAreaFrame
		
		window = MdiSubWindow()
		window.setWidget(frame)
		window.setWindowTitle(frame.title())
		window.setWindowIcon(self.get_icon(frame.icon()))
		window.windowStateChanged.connect(lambda old_state, new_state: self.on_window_state_changed(old_state, new_state, window))
		self._mdiarea.addSubWindow(window)
		window.show()
	
	def _add_outside_frame(self, frame, *args, **kwargs):
		# frame = AbstractOutsideFrame
		
		frame.setWindowTitle(frame.title())
		frame.setWindowIcon(self.get_icon(frame.icon()))
		self._outside_frames.append(frame)
		frame.show()
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	def close_all(self):
		
		for frame in self._outside_frames:
			frame.close()
		self._outside_frames = []
		self._mdiarea.closeAllSubWindows()
	
	def set_background_text(self, text):
		
		self._mdiarea._background_text = text
		self.hide()
		self.show()
	
	
	def add_query_frame(self, query, cmodel, cview):
		
		query_frame = QueryFrame(query, cmodel, cview)
		self._add_frame(query_frame)
		
		return query_frame
	
	def get_query_frames(self):
		
		for window in self._mdiarea.subWindowList():
			frame = window.widget()
			if isinstance(frame, QueryFrame):
				yield frame
	
	
	def add_external_frame(self, source, *args, **kwargs):
		
		external_frame = ExternalFrame(source, *args, **kwargs)
		self._add_frame(external_frame)
		
		return external_frame
	
	def get_external_frames(self):
		
		for window in self._mdiarea.subWindowList():
			frame = window.widget()
			if isinstance(frame, ExternalFrame):
				yield frame
	
	
	def add_class_graph_frame(self, cmodel, cview):
		
		class_graph_frame = ClassGraphFrame(cmodel, cview)
		self._add_frame(class_graph_frame)
		
		return class_graph_frame
	
	def get_class_graph_frames(self):
		
		for window in self._mdiarea.subWindowList():
			frame = window.widget()
			if isinstance(frame, ClassGraphFrame):
				yield frame
	
	
	def deselect_all(self):
		
		for frame in self._outside_frames:
			frame.on_deactivate()
		for window in self._mdiarea.subWindowList():
			window.widget().on_deactivate()
	
	def get_current_frame(self):
		
		current = self._mdiarea.currentSubWindow()
		if current:
			current = current.widget()
			if current:
				return current
		return None
	
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	@QtCore.Slot(object)
	def on_window_activated(self, window):
		
		self.signal_window_activated.emit(True)
	
	@QtCore.Slot(object, object, object)
	def on_window_state_changed(self, old_state, new_state, window):
		
		was_active = False
		is_active = False
		if old_state & QtCore.Qt.WindowState.WindowActive:
			was_active = True
		if new_state & QtCore.Qt.WindowState.WindowActive:
			is_active = True
		if was_active and not is_active:
			frame = window.widget()
			if frame is not None:
				frame.on_deactivate()
		if was_active != is_active:
			self.signal_window_activated.emit(is_active)

class MDIArea(QtWidgets.QMdiArea):
	
	def __init__(self, on_drag_enter, on_drag_move, on_drop):
		
		QtWidgets.QMdiArea.__init__(self)
		
		self._on_drag_enter = on_drag_enter
		self._on_drag_move = on_drag_move
		self._on_drop = on_drop
		self._background_text = ""
		
		self.setAcceptDrops(True)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
	
	def paintEvent(self, event):

		QtWidgets.QMdiArea.paintEvent(self, event)

		if self._background_text:
			painter = QtGui.QPainter()
			td = QtGui.QTextDocument()
			
			painter.begin(self.viewport())
			painter.translate(QtCore.QPointF(30, 30))
			
			font = td.defaultFont()
			font.setPointSize(10)
			td.setDefaultFont(font)
			td.setHtml(self._background_text)
			td.drawContents(painter)
			
			painter.end()
	
	def dragEnterEvent(self, event):
		
		self._on_drag_enter(event)
	
	def dragMoveEvent(self, event):
		
		self._on_drag_move(event)
	
	def dropEvent(self, event):
		
		self._on_drop(event)

class MdiSubWindow(QtWidgets.QMdiSubWindow):

	def __init__(self):
		
		QtWidgets.QMdiSubWindow.__init__(self, flags = QtCore.Qt.WindowType.SubWindow)
		
		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
	
	def closeEvent(self, *args, **kwargs):
		
		frame = self.widget()
		if frame is not None:
			frame.on_close()
		
		QtWidgets.QMdiSubWindow.closeEvent(self, *args, **kwargs)
