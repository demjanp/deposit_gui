from PySide2 import (QtWidgets, QtCore, QtGui)

class DConnectTabRecent(QtWidgets.QFrame):
	
	def __init__(self, parent):
		
		QtWidgets.QFrame.__init__(self, parent)
		
		self.parent = parent
		
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		self.left = QtWidgets.QFrame()
		self.left.setLayout(QtWidgets.QVBoxLayout())
		self.left.layout().setContentsMargins(0, 0, 0, 0)
		self.right = QtWidgets.QFrame()
		self.right.setLayout(QtWidgets.QVBoxLayout())
		self.right.layout().setContentsMargins(0, 0, 0, 0)
		
		self.recent_list = QtWidgets.QListWidget()
		self.recent_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.recent_list.itemSelectionChanged.connect(self.on_selected)
		self.recent_list.activated.connect(self.on_connect)
		
		self.connect_button = QtWidgets.QPushButton(self.parent.connect_caption())
		self.connect_button.clicked.connect(self.on_connect)
		
		self.clear_recent_button = QtWidgets.QPushButton("Clear Recent")
		self.clear_recent_button.clicked.connect(self.on_clear_recent)
		
		self.left.layout().addWidget(self.recent_list)
		self.left.layout().addWidget(self.connect_button)
		self.layout().addWidget(self.left)
		
		logo = self.parent.logo()
		if logo:
			self.right.layout().addWidget(logo)
			self.right.layout().addWidget(self.clear_recent_button)
			self.layout().addWidget(self.right)
		
		self.update()
	
	def set_recent_connections(self, data):
		# data = [[url], [identifier, connstr], ...]
		
		for row in data:
			name = None
			if len(row) == 1:
				url = row[0]
				name = "File: %s" % (url)
			elif len(row) == 2:
				identifier, connstr = row
				name = "DB: %s (%s)" % (identifier, connstr.split("@")[-1].split("?")[0])
			if not name:
				continue
			item = QtWidgets.QListWidgetItem(name)
			item.setData(QtCore.Qt.UserRole, row)
			self.recent_list.addItem(item)
		
		self.update()
	
	def has_items(self):
		
		return self.recent_list.count() > 0
	
	def update(self):
		
		self.connect_button.setEnabled(len(self.recent_list.selectedItems()) > 0)
	
	def on_selected(self):
		
		self.update()
	
	@QtCore.Slot()
	def on_connect(self):
		
		item = self.recent_list.currentItem()
		if not item:
			return
		row = item.data(QtCore.Qt.UserRole)
		if len(row) == 1:
			self.parent.on_connect(url = row[0])
			return
		
		if len(row) == 2:
			identifier, connstr = row
			self.parent.on_connect(identifier = identifier, connstr = connstr)
			return
	
	@QtCore.Slot()
	def on_clear_recent(self):
		
		self.recent_list.clear()
		self.parent.signal_clear_recent.emit()

