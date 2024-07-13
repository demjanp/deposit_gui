from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db import DConnectTabDB
from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db_rel import DConnectTabDBRel

from PySide6 import (QtWidgets, QtCore, QtGui)

class DSaveAsPostgresFrame(QtWidgets.QFrame):
	
	def __init__(self, dialog):
		
		QtWidgets.QFrame.__init__(self)
		
		self._dialog = dialog
		
		self.setMinimumWidth(600)
		self.setMinimumHeight(400)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.setStyleSheet('''
			QPushButton {margin: 3px 3px 3px 3px; padding: 5px 10px 5px 10px;}
		''')
		
		self._tab_db = DConnectTabDB(self)
		self._tab_dbrel = DConnectTabDBRel(self)
		
		self._tab_db.connect_button.hide()
		self._tab_db.delete_button.hide()
		self._tab_dbrel.connect_button.hide()
		self._tab_dbrel.delete_button.hide()
		
		self._tabs = QtWidgets.QTabWidget()
		self._tabs.addTab(self._tab_db, "PostgreSQL")
		self._tabs.addTab(self._tab_dbrel, "PostgreSQL Relational")
		
		self.layout().addWidget(self._tabs)
		
		self._dialog.set_title("Save As PostgreSQL")
		self._dialog.set_frame(self)
		self._dialog.setModal(True)
	
	def set_recent_connections(self, data):
		# data = [[url], [identifier, connstr], ...]
		
		self._tab_db.set_recent_connections(data)
		self._tab_dbrel.set_recent_connections(data)
	
	def on_connect(self, identifier = None, connstr = None, url = None, datasource = None):
		
		self._dialog.set_data(dict(
			identifier = identifier,
			connstr = connstr,
			url = url,
			datasource = datasource,
		))
		
		self._dialog.accept()
	
	def creating_enabled(self):
		
		return True
	
	def connect_caption(self):
		
		return "Connect"
