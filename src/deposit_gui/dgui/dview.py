'''
DView(DMainWindow).
	.registry
		.get(var)
		.set(var, value)
		.vars()
		.flush()
	.progress
		.cancel_pressed()
		.show(text = "")
		.update_state(text = None, value = None, maximum = None)
	.statusbar
		.message(text)
	.logging
		.logged = Signal(text: str)
		.get_log_path()
		.append(text)
		.flush()
	.set_title(name)
	.set_res_folder(path)
	.set_icon(name)
	.get_icon(name)
'''

from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.dgui.dmain_window import DMainWindow
from deposit_gui.dgui.dstatus_bar import DStatusBar
from deposit_gui.dgui.dprogress import DProgress
from deposit_gui.dgui.dlogging import DLogging

from PySide2 import (QtWidgets, QtCore, QtGui)
import traceback
import json
import sys
import os

class DView(AbstractSubview, DMainWindow):
	
	APP_NAME = "DView"
	REG_PREFIX = ""
	VERSION = "0.0.0"
	
	def __init__(self):
		
		self._current_geometry = None
		self._previous_geometry = None
		
		AbstractSubview.__init__(self)
		DMainWindow.__init__(self)
		
		self.progress = DProgress(self)
		self.statusbar = DStatusBar(self)
		self.logging = DLogging(self.APP_NAME, self.VERSION)
		
		self.set_title()
		self.setStatusBar(self.statusbar)
		
		sys.excepthook = self.exception_event
	
	
	# public methods
	
	def set_title(self, name: str = None) -> None:
		
		title = self.APP_NAME
		if name is None:
			self.setWindowTitle(title)
		else:
			self.setWindowTitle("%s - %s" % (name, title))
		
	def set_icon(self, name):
		
		self.setWindowIcon(self.get_icon(name))
	
	def get_recent_dir(self):
		
		return self.registry.get(self.REG_PREFIX + "recent_dir")
	
	def set_recent_dir(self, path):
		
		self.registry.set(self.REG_PREFIX + "recent_dir", path)
	
	def get_recent_connections(self):
		
		rows = self.registry.get(self.REG_PREFIX + "recent")
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
		self.registry.set(self.REG_PREFIX + "recent", json.dumps(data))
	
	def clear_recent_connections(self):
		
		self.registry.set(self.REG_PREFIX + "recent", "")
	
	
	# events
	
	def exception_event(self, typ, value, tb):
		
		text = "Exception: %s: %s\nTraceback: %s" % (
			str(typ), str(value)[:512], "".join(traceback.format_tb(tb))
		)
		self.logging.append(text)
		print(text)
	
	
	# overriden QMainWindow methods
	
	def keyPressEvent(self, event):
		
		for action in self.findChildren(QtWidgets.QAction):
			if action.isEnabled() and (
				action.shortcut() == QtGui.QKeySequence(
					event.key()+int(event.modifiers())
				)
			):
				action.trigger()
		
		QtWidgets.QMainWindow.keyPressEvent(self, event)
	
	def closeEvent(self, event):
		
		DMainWindow.closeEvent(self, event)

