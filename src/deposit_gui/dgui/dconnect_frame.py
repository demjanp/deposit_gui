from deposit_gui.dgui.dconnect_tabs.dconnect_tab_recent import DConnectTabRecent
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_pickle import DConnectTabPickle
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_json import DConnectTabJSON
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db import DConnectTabDB
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db_rel import DConnectTabDBRel
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_memory import DConnectTabMemory

from PySide6 import (QtWidgets, QtCore, QtGui)
from pathlib import Path
import os

class DConnectFrame(QtWidgets.QFrame):
	
	signal_clear_recent = QtCore.Signal()
	
	def __init__(self, dialog):
		
		QtWidgets.QFrame.__init__(self)
		
		self._dialog = dialog
		
		self._recent_dir = str(Path.home())
		
		self.setMinimumWidth(600)
		self.setMinimumHeight(400)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.setStyleSheet('''
			QPushButton {margin: 3px 3px 3px 3px; padding: 5px 10px 5px 10px;}
		''')
		
		self._tab_recent = DConnectTabRecent(self)
		self._tab_pickle = DConnectTabPickle(self)
		self._tab_json = DConnectTabJSON(self)
		self._tab_db = DConnectTabDB(self)
		self._tab_dbrel = DConnectTabDBRel(self)
		
		self._tabs = QtWidgets.QTabWidget()
		self._tabs.addTab(self._tab_recent, "Recent")
		self._tabs.addTab(self._tab_pickle, "Pickle")
		self._tabs.addTab(self._tab_json, "JSON")
		self._tabs.addTab(self._tab_db, "PostgreSQL")
		self._tabs.addTab(self._tab_dbrel, "PostgreSQL Relational")
		if self.creating_enabled():
			self.tab_memory = DConnectTabMemory(self)
			self._tabs.addTab(self.tab_memory, "Memory")
		
		self.layout().addWidget(self._tabs)
		
		self._dialog.set_title(self.title())
		self._dialog.set_frame(self)
		self._dialog.setModal(True)
	
	def set_recent_dir(self, path):
		
		self._recent_dir = path
		self._tab_pickle.set_current_dir(self._recent_dir)
		self._tab_json.set_current_dir(self._recent_dir)
	
	def get_recent_dir(self):
		
		return self._recent_dir
	
	def set_recent_connections(self, data):
		# data = [[url], [identifier, connstr], ...]
		
		self._tab_recent.set_recent_connections(data)
		self._tab_db.set_recent_connections(data)
		self._tab_dbrel.set_recent_connections(data)
		if self._tab_recent.has_items():
			self._tabs.setCurrentIndex(0)
	
	def on_connect(self, identifier = None, connstr = None, url = None, datasource = None):
		
		self._dialog.set_data(dict(
			identifier = identifier,
			connstr = connstr,
			url = url,
			datasource = datasource,
		))
		
		self._dialog.accept()
	
	def title(self):
		# re-implement
		
		return "Connect"
	
	def creating_enabled(self):
		# re-implement
		
		return False
	
	def connect_caption(self):
		# re-implement
		
		return "Connect"
	
	def logo(self):
		# re-implement
		
		return None

