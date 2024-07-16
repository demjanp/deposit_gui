from deposit.datasource import DB
from deposit import Store

from deposit.utils.fnc_serialize import (parse_connstr)

from PySide6 import (QtWidgets, QtCore, QtGui)
from natsort import natsorted

class DConnectTabDB(QtWidgets.QFrame):
	
	DATASOURCE = DB
	
	def __init__(self, parent):
		
		QtWidgets.QFrame.__init__(self, parent)
		
		self._can_load = False
		self._can_create = False
		
		self.datasource = self.DATASOURCE()
		
		self.parent = parent
		
		self.form = QtWidgets.QWidget()
		layout_form = QtWidgets.QFormLayout()
		self.form.setLayout(layout_form)

		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(10, 10, 10, 10)
		
		self.host_combo = QtWidgets.QComboBox()
		self.host_combo.setEditable(True)
		self.host_combo.editTextChanged.connect(self.on_host_changed)
		self.dbname_combo = QtWidgets.QComboBox()
		self.dbname_combo.setEditable(True)
		self.dbname_combo.editTextChanged.connect(self.update)
		self.schema_combo = QtWidgets.QComboBox()
		self.schema_combo.setEditable(True)
		self.schema_combo.setCurrentText("public")
		self.schema_combo.editTextChanged.connect(self.update)
		self.user_edit = QtWidgets.QLineEdit("")
		self.user_edit.textChanged.connect(self.update)
		self.pass_edit = QtWidgets.QLineEdit("")
		self.pass_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self.pass_edit.textChanged.connect(self.update)
		self.identifier_combo = QtWidgets.QComboBox()
		self.identifier_combo.setEditable(True)
		self.identifier_combo.editTextChanged.connect(self.on_identifier_changed)
		self.identifier_combo.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		
		self.connect_button = QtWidgets.QPushButton(self.parent.connect_caption())
		self.connect_button.setEnabled(False)
		self.connect_button.clicked.connect(self.on_connect)
		
		self.create_button = QtWidgets.QPushButton("Create")
		self.create_button.setEnabled(False)
		self.create_button.clicked.connect(self.on_create)
		
		self.delete_button = QtWidgets.QPushButton("Delete")
		self.delete_button.setEnabled(False)
		self.delete_button.clicked.connect(self.on_delete)
		
		self.form.layout().addRow("Host[:port]:", self.host_combo)
		self.form.layout().addRow("Database:", self.dbname_combo)
		self.form.layout().addRow("Schema:", self.schema_combo)
		self.form.layout().addRow("Username:", self.user_edit)
		self.form.layout().addRow("Password:", self.pass_edit)
		self.form.layout().addRow("Identifier:", self.identifier_combo)
		
		button_container = QtWidgets.QWidget()
		layout_button_container = QtWidgets.QHBoxLayout()
		button_container.setLayout(layout_button_container)
		button_container.layout().setContentsMargins(0, 0, 0, 0)
		button_container.layout().addStretch()
		button_container.layout().addWidget(self.connect_button)
		button_container.layout().addWidget(self.create_button)
		button_container.layout().addWidget(self.delete_button)
		button_container.layout().addStretch()
		
		self.layout().addWidget(self.form)
		self.layout().addWidget(button_container)
		self.layout().addStretch()
		
		self._update_timer = QtCore.QTimer()
		self._update_timer.setSingleShot(True)
		self._update_timer.timeout.connect(self.on_update_timer)
	
	def set_recent_connections(self, data):
		# data = [[url], [identifier, connstr], ...]
		
		hosts = []
		logins = []
		dbnames = {}  # {host: [dbname, ...], ...}
		for row in data:
			if len(row) != 2:
				continue
			identifier, connstr = row
			parsed = parse_connstr(connstr)
			if not parsed:
				continue
			username = parsed["username"]
			password = parsed["password"]
			host = parsed["host"]
			dbname = parsed["dbname"]
			schema = parsed["schema"]
			if host not in dbnames:
				dbnames[host] = []
			if dbname not in dbnames[host]:
				dbnames[host].append(dbname)
			if host not in hosts:
				hosts.append(host)
				logins.append([username, password])
		self.host_combo.blockSignals(True)
		self.host_combo.addItem("")
		for i, host in enumerate(hosts):
			self.host_combo.addItem(host, [host] + logins[i] + [dbnames[host]])
		self.host_combo.blockSignals(False)
	
	def get_values(self):
		
		host = self.host_combo.currentText().strip()
		dbname = self.dbname_combo.currentText().strip()
		schema = self.schema_combo.currentText().strip()
		user = self.user_edit.text().strip()
		password = self.pass_edit.text().strip()
		identifier = self.identifier_combo.currentText().strip()
		if host and (":" not in host):
			host = "%s:5432" % (host)
		return host, dbname, schema, user, password, identifier
	
	@QtCore.Slot()
	def on_host_changed(self):
		
		data = self.host_combo.currentData()
		host = self.host_combo.currentText().strip()
		if data:
			host, username, password, dbnames = data
			_, curr_name, curr_schema, curr_user, curr_password, _ = self.get_values()
			if not (curr_user or curr_password):
				curr_user, curr_password = username, password
				self.user_edit.blockSignals(True)
				self.pass_edit.blockSignals(True)
				self.user_edit.setText(username)
				self.pass_edit.setText(password)
				self.user_edit.blockSignals(False)
				self.pass_edit.blockSignals(False)
			if dbnames:
				self.dbname_combo.blockSignals(True)
				self.dbname_combo.clear()
				self.dbname_combo.addItems(dbnames)
				if curr_name:
					self.dbname_combo.setCurrentText(curr_name)
				self.dbname_combo.blockSignals(False)
		self.update()
	
	@QtCore.Slot()
	def on_identifier_changed(self):
		
		self.update()
	
	@QtCore.Slot()
	def on_ident_load(self):
		
		self.on_update_timer()
	
	@QtCore.Slot()
	def update(self):
		
		self.connect_button.setEnabled(False)
		self.create_button.setEnabled(False)
		self.delete_button.setEnabled(False)
		
		self._update_timer.start(1000)
	
	@QtCore.Slot()
	def on_update_timer(self):
		
		host, dbname, schema, user, password, identifier = self.get_values()
		schemas = []
		identifiers = []
		if "" not in [host, dbname, schema, user, password]:
			self.datasource.set_username(user)
			self.datasource.set_password(password)
			self.datasource.set_host(host)
			self.datasource.set_database(dbname)
			self.datasource.connect()
			
			schemas = self.datasource.get_schemas()
			if schemas and not schema:
				schema = schemas[0]
			self.datasource.set_schema(schema)
			
			identifiers = natsorted(self.datasource.get_identifiers().keys())
			if identifiers and not identifier:
				identifier = identifiers[0]
			self.datasource.set_identifier(identifier)
		
		self.schema_combo.blockSignals(True)
		self.schema_combo.clear()
		self.schema_combo.addItems(schemas)
		if schema:
			self.schema_combo.setCurrentText(schema)
		self.schema_combo.blockSignals(False)
		
		self.identifier_combo.blockSignals(True)
		self.identifier_combo.clear()
		self.identifier_combo.addItems(identifiers)
		if identifier:
			self.identifier_combo.setCurrentText(identifier)
		self.identifier_combo.blockSignals(False)
		
		self._can_load = self.datasource.is_valid()
		self._can_create = (identifier != "") and self.parent.creating_enabled() and self.datasource.can_create()
		
		self.datasource.disconnect()
		
		self.connect_button.setEnabled(self._can_load)
		self.create_button.setEnabled(self._can_load or self._can_create)
		self.delete_button.setEnabled(self._can_load)
	
	@QtCore.Slot()
	def on_connect(self):
		
		if self._can_load:
			self.parent.on_connect(identifier = self.datasource.get_identifier(), connstr = self.datasource.get_connstr())
	
	@QtCore.Slot()
	def on_create(self):
		
		if self._can_load:
			reply = QtWidgets.QMessageBox.question(self, "Confirm Overwrite", "Are you sure you want to overwrite the database?<br>All data will be lost!")
			if reply != QtWidgets.QMessageBox.StandardButton.Yes:
				return
		
		if self._can_create:
			self.datasource.create()
			store = Store(keep_temp = True)
			folder = QtWidgets.QFileDialog.getExistingDirectory(self, caption = "Select Local Folder")
			if not folder:
				return
			store.set_local_folder(folder)
			self.datasource.save(store)
			self.parent.on_connect(identifier = self.datasource.get_identifier(), connstr = self.datasource.get_connstr(), datasource = self.datasource)
			return
	
	@QtCore.Slot()
	def on_delete(self):
		
		if self._can_load:
			reply = QtWidgets.QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete the database?")
			if reply != QtWidgets.QMessageBox.StandardButton.Yes:
				return
		
		self.datasource.delete()
		self.update()

