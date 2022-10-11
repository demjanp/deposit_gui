from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.dgui.dmain_window import DMainWindow
from deposit_gui.dgui.dstatus_bar import DStatusBar
from deposit_gui.dgui.dprogress import DProgress
from deposit_gui.dgui.dlogging import DLogging

from deposit.utils.fnc_serialize import (
	encrypt_connstr,
	decrypt_connstr,
)

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
			rows = json.loads(rows)
			collect = []
			for row in rows:
				if len(row) == 2:
					identifier, connstr = row
					collect.append([identifier, decrypt_connstr(connstr)])
				else:
					collect.append(row)
			return collect
		return []
	
	def add_recent_connection(self, url = None, identifier = None, connstr = None):
		
		data = self.get_recent_connections()
		row = None
		if url is not None:
			row = [url]
		elif (identifier is not None) and (connstr is not None):
			row = [identifier, encrypt_connstr(connstr)]
		if row is None:
			return
		if row in data:
			data.remove(row)
		data = [row] + data
		self.registry.set(self.REG_PREFIX + "recent", json.dumps(data))
	
	def clear_recent_connections(self):
		
		self.registry.set(self.REG_PREFIX + "recent", "")
	
	def get_active_window(self):
		
		active = self
		for window in QtWidgets.QApplication.topLevelWidgets():
			if not isinstance(window, QtWidgets.QMainWindow):
				continue
			if window.isActiveWindow():
				active = window
				break
		return active
	
	
	def show_information(self, caption, text):
		
		QtWidgets.QMessageBox.information(
			self.get_active_window(), caption, text
		)
	
	def show_warning(self, caption, text):
		
		QtWidgets.QMessageBox.warning(self.get_active_window(), caption, text)
	
	def show_question(self, caption, text):
		
		reply = QtWidgets.QMessageBox.question(
			self.get_active_window(), caption, text
		)
		
		return reply == QtWidgets.QMessageBox.Yes
	
	def show_input_dialog(self, caption, text, value = "", **kwargs):
		
		text, ok = QtWidgets.QInputDialog.getText(
			self.get_active_window(), caption, text, text = value, **kwargs
		)
		if text and ok:
			return text
		return None
	
	def show_item_dialog(self, caption, text, items, editable = False):
		
		name, ok = QtWidgets.QInputDialog.getItem(
			self.get_active_window(), caption, text, items, editable
		)
		if name and ok:
			return name
		return None
	
	
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

