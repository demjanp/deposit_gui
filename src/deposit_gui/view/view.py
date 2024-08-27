from deposit_gui.dgui.dview import DView
from deposit_gui.dgui.dprogress import DProgress

from deposit_gui import __version__, __title__

from PySide6 import (QtWidgets, QtCore, QtGui)
import sys

class View(DView):
	
	APP_NAME = __title__
	VERSION = __version__
	
	def __init__(self, vnavigator, vmdiarea) -> None:
		
		DView.__init__(self)
		
		self._close_callback = None
		
		central_widget = QtWidgets.QWidget(self)
		central_widget_layout = QtWidgets.QVBoxLayout()
		central_widget.setLayout(central_widget_layout)
		central_widget_layout.setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(central_widget)
		
		self._tool_window = QtWidgets.QMainWindow()
		self._tool_window.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
		central_widget_layout.addWidget(self._tool_window)
		
		splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
		splitter.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		central_widget_layout.addWidget(splitter)
		
		left_frame = QtWidgets.QFrame()
		left_frame_layout = QtWidgets.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		left_frame_layout.setContentsMargins(0, 0, 0, 0)
		
		splitter.addWidget(vnavigator)
		splitter.addWidget(vmdiarea)
		
		if sys.platform == "win32":
			self.set_app_icon("dep_cube.svg")
		elif sys.platform in ["linux", "linux2"]:
			self.set_app_icon("deposit_icon.png")
		elif sys.platform == "darwin":
			self.set_app_icon("deposit_icon.icns")
		else:
			raise Exception("Operating system not supported")
		
		self.update_style()
	
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
		
		if self._close_callback is not None:
			if not self._close_callback():
				event.ignore()
				return
		DView.closeEvent(self, event)
