from deposit.utils.fnc_serialize import (dtype_to_dict, value_to_dtype)

from PySide6 import (QtWidgets, QtCore, QtGui)

class QueryItem(object):
	
	def __init__(self, index, class_name = None, descriptor_name = None, obj_id = None, value = None, icons = None, read_only = False, obj_id_row = None):
		
		self.index = index
		self.row = None if index is None else index.row()
		self.column = None if index is None else index.column()
		self.class_name = class_name
		self.descriptor_name = descriptor_name
		self.obj_id = obj_id
		self.obj_id_row = obj_id_row
		self.value = value
		self.read_only = read_only
		self.datasource = {}
		
		self._icons = icons
		self._data = {}
		
		if (self.class_name is None) or (self.descriptor_name is None):
			self.read_only = True
		if self.value.__class__.__name__ in ["DResource", "DGeometry"]:
			self.read_only = True
		if self.obj_id != self.obj_id_row:
			self.read_only = True
	
	def to_dict(self):
		
		return dict(
			row = self.index.row(),
			column = self.index.column(),
			class_name = self.class_name,
			descriptor_name = self.descriptor_name,
			obj_id = self.obj_id,
			obj_id_row = self.obj_id_row,
			value = dtype_to_dict(self.value),
			read_only = self.read_only,
			datasource = self.datasource,
		)
	
	def from_dict(self, data):
		
		self.row = data.get("row", None)
		self.column = data.get("column", None)
		self.class_name = data.get("class_name", None)
		self.descriptor_name = data.get("descriptor_name", None)
		self.obj_id = data.get("obj_id", None)
		self.obj_id_row = data.get("obj_id_row", None)
		self.value = value_to_dtype(data.get("value", None))
		self.read_only = data.get("read_only", False)
		self.datasource = data.get("datasource", {})
		
		return self
	
	def is_object(self):
		
		return (self.obj_id is not None) and (self.descriptor_name is None)
	
	def is_datetime(self):
		
		return self.value.__class__.__name__ == "DDateTime"
	
	def is_geometry(self):
		
		return self.value.__class__.__name__ == "DGeometry"
		
	def is_resource(self):
		
		return self.value.__class__.__name__ == "DResource"
	
	def populate_data(self, role):
		
		if role in [QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole]:
			
			role2 = QtCore.Qt.ItemDataRole.EditRole if role == QtCore.Qt.ItemDataRole.DisplayRole else QtCore.Qt.ItemDataRole.DisplayRole
			if role2 in self._data:
				self._data[role] = self._data[role2]
			
			if self.is_object():
				self._data[role] = "ID: %d" % (self.obj_id)
				return
			
			if self.is_datetime():
				self._data[role] = self.value.isoformat
				return
			
			if self.is_geometry():
				self._data[role] = self.value.geometry_type
				return
			
			if self.is_resource():
				self._data[role] = self.value.filename
				return
			
			if self.value is None:
				self._data[role] = ""
				return
			
			self._data[role] = str(self.value)
			return
		
		if role == QtCore.Qt.ItemDataRole.DecorationRole:
			
			if self.value is None:
				self._data[role] = None
				return
			
			if self.is_object() and (self._icons is not None):
				self._data[role] = self._icons["obj"]
				return
			
			if self.is_geometry() and (self._icons is not None):
				self._data[role] = self._icons["geo"]
				return
			
			if self.is_resource():
				
				if self.value.is_image:
					
					if self.value.is_stored and (self._icons is not None):
						self._data[role] = self._icons["image"]
						return
					
					if  self._icons is not None:
						self._data[role] = self._icons["remote_image"]
						return
				
				if self.value.is_stored and (self._icons is not None):
					self._data[role] = self._icons["file"]
					return
				
				if  self._icons is not None:
					self._data[role] = self._icons["remote_file"]
					return
				
				self._data[role] = None
				return
			
			self._data[role] = None
			return
		
		if role == QtCore.Qt.ItemDataRole.UserRole:
			
			self._data[role] = self
			return
		
		if role == QtCore.Qt.ItemDataRole.BackgroundRole:
			
			if self.read_only:
				self._data[role] = QtGui.QColor(240, 240, 240, 255)
				return
			
			self._data[role] = None
			return
		
		self._data[role] = None
		return
	
	def data(self, role):
		
		if role not in self._data:
			self.populate_data(role)
		return self._data[role]
	
	def get_display_data(self):
		
		return self.data(QtCore.Qt.ItemDataRole.DisplayRole)
	
	def __repr__(self):
		
		return "QueryItem(r: %d, c: %d, Class: %s, Descriptor: %s, Object: %s, Row Object: %s, Value: %s, Read Only: %s)" % (
			self.row, self.column, self.class_name, self.descriptor_name, self.obj_id, self.obj_id_row, str(self.value), self.read_only
		)