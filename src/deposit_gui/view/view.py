from deposit_gui.dgui.dview import DView

from deposit_gui import __version__, __title__

from PySide2 import (QtWidgets, QtCore, QtGui)

class View(DView):
	
	APP_NAME = __title__
	VERSION = __version__
	
	def __init__(self, vnavigator, vmdiarea) -> None:
		
		DView.__init__(self)
		
		self._close_callback = None
		
		central_widget = QtWidgets.QWidget(self)
		central_widget.setLayout(QtWidgets.QVBoxLayout())
		central_widget.layout().setContentsMargins(0, 0, 0, 0)
		self.setCentralWidget(central_widget)
		
		self._tool_window = QtWidgets.QMainWindow()
		self._tool_window.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
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
