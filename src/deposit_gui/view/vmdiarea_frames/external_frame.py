from deposit_gui.view.vmdiarea_frames.abstract_mdiarea_frame import AbstractMDIAreaFrame
from deposit import externalsource as Externalsource
from deposit import DGeometry
from deposit.query.parse import (remove_bracketed_all, replace_bracketed)

from PySide6 import (QtWidgets, QtCore, QtGui)

class ExternalFrame(AbstractMDIAreaFrame, QtWidgets.QWidget):
	
	def __init__(self, source, *args, **kwargs):
		
		AbstractMDIAreaFrame.__init__(self)
		QtWidgets.QWidget.__init__(self)
		
		self.tabs = None
		self.sheet = None

		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.layout().setContentsMargins(0, 0, 0, 0)
		self.layout().setSpacing(0)
		
		if not hasattr(Externalsource, source):
			raise Exception("External source not supported: %s" % (source))
		self._externalsource = getattr(Externalsource, source)()
		self._externalsource.load(*args, **kwargs)
		
		sheets = self._externalsource.sheets()
		if len(sheets) > 1:
			self.tabs = QtWidgets.QTabWidget()
			self.layout().addWidget(self.tabs)
			for sheet_name in sheets:
				self.tabs.addTab(
					ExternalSheet(
						ExternalHeader(self._externalsource, sheet_name),
						ExternalBody(self, self._externalsource, sheet_name)
					),
					sheet_name
				)
		else:
			self.sheet = ExternalSheet(
						ExternalHeader(self._externalsource, sheets[0]),
						ExternalBody(self, self._externalsource, sheets[0])
					)
			self.layout().addWidget(self.sheet)
	
	def title(self):
		
		if self._externalsource is None:
			return "External Source"
		return self._externalsource.get_name()
	
	def icon(self):
		
		return "dep_cube.svg"
	
	def get_current(self):
		
		if self.tabs is not None:
			return self.tabs.currentWidget()
		return self.sheet
	
	def get_current_header(self):
		
		return self.get_current().header
	
	def get_current_body(self):
		
		return self.get_current().body
	
	def get_targets(self):
		# returns {column_idx: (class_name, descriptor_name), ...}
		
		header = self.get_current_header()
		targets = {}
		for idx in range(self._externalsource.column_count(header.sheet_name())):
			substr, bracketed = remove_bracketed_all(header.item(0, idx).data(QtCore.Qt.ItemDataRole.DisplayRole))
			data = substr.split(".")
			if len(data) != 2:
				continue
			data = [replace_bracketed(name, bracketed).strip("[]") for name in data]
			targets[idx] = tuple(data)
			
		return targets
	
	def get_column_count(self):
		
		if self._externalsource is None:
			return 0
		return self._externalsource.column_count(self.get_current_header().sheet_name())
	
	def get_row_count(self):
		
		if self._externalsource is None:
			return 0
		return self._externalsource.row_count(self.get_current_header().sheet_name())
	
	def get_data(self, row, col):
		
		if self._externalsource is None:
			return None
		
		return self._externalsource.data(self.get_current_header().sheet_name(), row, col)
	
	def on_close(self):
		# re-implement
		
		pass
	
	def on_deactivate(self):
		# re-implement
		
		pass

class ExternalSheet(QtWidgets.QWidget):
	
	def __init__(self, header, body):
		
		self.header = header
		self.body = body
		
		QtWidgets.QWidget.__init__(self)
		
		self.verticalLayout = QtWidgets.QVBoxLayout()
		self.verticalLayout.setContentsMargins(0, 0, 0, 0)
		self.verticalLayout.setSpacing(0)
		self.setLayout(self.verticalLayout)
		
		self.verticalLayout.addWidget(self.header)
		self.verticalLayout.addWidget(self.body)
		
		self.header.horizontalScrollBar().valueChanged.connect(self.on_horizontalScroll)
		self.body.horizontalScrollBar().valueChanged.connect(self.on_horizontalScroll)
		self.header.horizontalHeader().sectionResized.connect(self.on_sectionResized)

	def on_horizontalScroll(self, position):
		
		self.header.horizontalScrollBar().setSliderPosition(position)
		self.body.horizontalScrollBar().setSliderPosition(position)
		
	def on_sectionResized(self, index, oldSize, newSize):
		
		self.body.horizontalHeader().resizeSection(index, newSize)

class ExternalHeader(QtWidgets.QTableWidget):
	
	def __init__(self, externalsource, sheet):
		
		QtWidgets.QTableWidget.__init__(self)
		
		self._externalsource = externalsource
		self._sheet = sheet
		
		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		self.verticalHeader().setVisible(False)
		
		columns_n = self._externalsource.column_count(self._sheet)
		self.setRowCount(1)
		self.setColumnCount(columns_n)
		for idx in range(columns_n):
			name = self._externalsource.column_name(self._sheet, idx)
			# set column label
			item = QtWidgets.QTableWidgetItem()
			item.setData(QtCore.Qt.ItemDataRole.DisplayRole, name)
			self.setHorizontalHeaderItem(idx, item)
			
			# set target
			item = QtWidgets.QTableWidgetItem()
			item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsEditable)
			item.setData(QtCore.Qt.ItemDataRole.DisplayRole, name)
			self.setItem(0, idx, item)
		
		self.adjustSize()
	
	def sheet_name(self):
		
		return self._sheet
		
class ExternalBody(QtWidgets.QTableWidget):
	
	def __init__(self, externalframe, externalsource, sheet = "0"):
		
		QtWidgets.QTableWidget.__init__(self)
		
		self._externalframe = externalframe
		self._externalsource = externalsource
		self._sheet = sheet
		
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
		self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.horizontalHeader().setVisible(False)
		self.verticalHeader().setVisible(False)
		
		rows_n = self._externalsource.row_count(self._sheet)
		
		if not rows_n:
			return
		
		columns_n = self._externalsource.column_count(self._sheet)
		
		self.setRowCount(rows_n)
		self.setColumnCount(columns_n)
		
		for row_idx in range(rows_n):
			for column_idx in range(columns_n):
				data = self._externalsource.data(self._sheet, row_idx, column_idx)
				
				item = QtWidgets.QTableWidgetItem()
				item.setData(QtCore.Qt.ItemDataRole.UserRole, data)
				if isinstance(data, DGeometry):
					item.setData(QtCore.Qt.ItemDataRole.DisplayRole, data.geometry_type)
					item.setData(QtCore.Qt.ItemDataRole.DecorationRole, self._externalframe.get_icon("geometry.svg"))
				else:
					item.setData(QtCore.Qt.ItemDataRole.DisplayRole, data)
				item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
				
				self.setItem(row_idx, column_idx, item)
		
		self.adjustSize()


