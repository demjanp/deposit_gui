from deposit.utils.fnc_files import (as_url)
from deposit import Store

from PySide6 import (QtWidgets, QtCore, QtGui)
import os

class AbstractTabFile(QtWidgets.QFrame):
	
	EXTENSION = ""  # json, pickle etc.
	DATASOURCE = None
	
	def __init__(self, parent):
		
		QtWidgets.QFrame.__init__(self, parent)
		
		self.parent = parent
		
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		
		homedir = self.parent.get_recent_dir()
		rootdir, _ = os.path.splitdrive(homedir)
		if not rootdir:
			rootdir = homedir
		
		self.fs_model = QtWidgets.QFileSystemModel()
		self.fs_model.setRootPath(rootdir)
		self.fs_model.setNameFilters(["*.%s" % self.EXTENSION])
		self.fs_model.setNameFilterDisables(False)
		self.tree = FileTree()
		self.tree.setModel(self.fs_model)
		self.set_current_dir(homedir)
		self.tree.setAnimated(False)
		self.tree.setIndentation(20)
		self.tree.setSortingEnabled(True)
		self.tree.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
		self.tree.selected.connect(self.on_selected)
		self.tree.activated.connect(self.on_connect)
		
		self.path_edit = QtWidgets.QLineEdit()
		self.path_edit.textChanged.connect(self.on_path_changed)
		
		self.connect_button = QtWidgets.QPushButton(self.parent.connect_caption())
		self.connect_button.clicked.connect(self.on_connect)
		
		self.layout().addWidget(self.tree)
		self.layout().addWidget(self.path_edit)
		self.layout().addWidget(self.connect_button)
		
		self.update()
	
	def set_current_dir(self, path):
		
		for i in range(1, self.fs_model.columnCount()):
			self.tree.hideColumn(i)
		self.tree.setCurrentIndex(self.fs_model.index(path))
		self.tree.setExpanded(self.fs_model.index(path), True)
	
	def get_path(self):
		
		path = self.path_edit.text().strip()
		if (not path) or os.path.isdir(path):
			return ""
		path, filename = os.path.split(path)
		filename, ext = os.path.splitext(filename)
		if ext.lower() != ".%s" % self.EXTENSION:
			ext = ".%s" % self.EXTENSION
		path = os.path.join(path, "%s%s" % (filename, ext))
		return path
	
	def update(self):
		
		path = self.get_path()
		is_valid = False
		if os.path.isfile(path):
			self.connect_button.setText(self.parent.connect_caption())
			is_valid = True
		elif self.parent.creating_enabled():
			self.connect_button.setText("Create")
			is_valid = True
		self.connect_button.setEnabled(is_valid and (path != ""))
	
	@QtCore.Slot()
	def on_selected(self):
		
		index = self.tree.currentIndex()
		path = self.fs_model.filePath(index)
		self.path_edit.setText(path)
	
	@QtCore.Slot()
	def on_path_changed(self):
		
		self.update()
	
	@QtCore.Slot()
	def on_connect(self):
		
		path = self.get_path()
		if not path:
			return
		
		if (not os.path.isfile(path)) and (not self.parent.creating_enabled()):
			QtWidgets.QMessageBox.critical(self, "Error", "Could not create database.")
			return None
		
		if not os.path.isfile(path):
			store = Store(keep_temp = True)
			store.save(path = path)
		
		url = as_url(path)
		self.parent.on_connect(url = url)

class FileTree(QtWidgets.QTreeView):
	
	selected = QtCore.Signal()
	
	def selectionChanged(self, selected, deselected):
		
		self.selected.emit()
		
		QtWidgets.QTreeView.selectionChanged(self, selected, deselected)

