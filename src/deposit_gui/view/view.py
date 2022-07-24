from deposit_gui.dgui.dview import DView

from deposit_gui import __version__, __title__

from PySide2 import (QtWidgets, QtCore, QtGui)
import json

class View(DView):
	
	APP_NAME = __title__
	VERSION = __version__
	
	signal_close = QtCore.Signal()
	
	def __init__(self, vnavigator, vmdiarea) -> None:
		
		DView.__init__(self)
		
		central_widget = QtWidgets.QWidget(self)
		central_widget.setLayout(QtWidgets.QVBoxLayout())
		central_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(central_widget)
		
		self._tool_window = QtWidgets.QMainWindow()
		central_widget.layout().addWidget(self._tool_window)
		
		splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
		splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		central_widget.layout().addWidget(splitter)
		
		left_frame = QtWidgets.QFrame()
		left_frame.setLayout(QtWidgets.QVBoxLayout())
		left_frame.layout().setContentsMargins(0, 0, 0, 0)
		
		splitter.addWidget(vnavigator)
		splitter.addWidget(vmdiarea)
		
		self.setWindowIcon(self.get_icon("dep_cube.svg"))
		
	def get_recent_dir(self):
		
		return self.registry.get("recent_dir")
	
	def set_recent_dir(self, path):
		
		self.registry.set("recent_dir", path)
	
	def get_recent_connections(self):
		
		rows = self.registry.get("recent")
		if rows:
			return json.loads(rows)
		return []
	
	def add_recent_connection(self, url = None, identifier = None, connstr = None):
		
		data = self.get_recent_connections()
		row = None
		if url is not None:
			row = [url]
		elif (identifier is not None) and (connstr is not None):
			row = [identifier, connstr]
		if row is None:
			return
		if row in data:
			data.remove(row)
		data = [row] + data
		self.registry.set("recent", json.dumps(data))
	
	def clear_recent_connections(self):
		
		self.registry.set("recent", "")
	
	def update_model_info(self):
		
		pass
	
	def menuBar(self):
		# HACK to stop MDI Subwindows move controls to MenuBar when maximized
		
		return self._tool_window.menuBar()
	
	def addToolBar(self, title):
		# HACK to stop MDI Subwindows move controls to MenuBar when maximized
		
		return self._tool_window.addToolBar(title)
	
	def addToolBarBreak(self, *args, **kwargs):
		# HACK to stop MDI Subwindows move controls to MenuBar when maximized
		
		self._tool_window.addToolBarBreak(*args, **kwargs)
	
	def closeEvent(self, event):
		
		self.signal_close.emit()
		DView.closeEvent(self, event)

