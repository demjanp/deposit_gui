from deposit_gui.dgui.dcactions import DCActions
from deposit_gui.view.vmdiarea_frames.external_frame import ExternalFrame
from deposit_gui.view.vmdiarea_frames.query_frame import QueryFrame

from deposit import externalsource as Externalsource
from deposit.utils.fnc_files import (as_url, sanitize_filename, get_temp_path)
from deposit.utils.fnc_serialize import (value_to_str)

from PySide2 import (QtWidgets, QtGui, QtCore)
from collections import defaultdict
from natsort import natsorted
import os

class CActions(DCActions):
	
	def __init__(self, cmain, cview) -> None:
		
		DCActions.__init__(self, cmain, cview)
		
		self._relation_label = ""
		
		self.update()
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	
	# ---- Actions
	# ------------------------------------------------------------------------
	def set_up_tool_bar(self):
		
		return {
			"Data": [
				("Connect", "Connect"),
				("Save", "Save"),
			],
			"Edit": [
				("Copy", "Copy"),
				("Paste", "Paste"),
				None,
				("AddRelation", "Add Relation"),
				("RelationName", ""),
				("RemoveRelation", "Remove Relation"),
				("ClassGraph", "Class Relations"),
				None,
				("FieldCalculator", "Field Calculator"),
				("MergeRows", "Merge Rows"),
				("MergeIdentical", "Merge Identical Rows"),
				("Duplicate", "Duplicate Row"),
			],
			"External": [
				("ImportDeposit", "Import from Deposit"),
				("ExportDeposit", "Export to Deposit"),
				None,
				("LoadExternal", "Load External Data"),
				("ImportExternal", "Import Data"),
				("ExportExternal", "Export Data"),
			]
		}
	
	def set_up_menu_bar(self):
		
		return {
			"Data": [
				("Connect", "Connect"),
				("Save", "Save"),
				("SaveAsFile", "Save As File"),
				("SaveAsPostgres", "Save As PostgreSQL"),
				None,
				("AutoBackup", "Backup database after every save"),
				None,
				("ImportDeposit", "Import from Deposit"),
				("ExportDeposit", "Export to Deposit"),
				("LoadExternal", "Load External"),
				("ExportExternal", "Export Data"),
				None,
				("SetLocalFolder", "Set Local Folder"),
				("ClearLocalFolder", "Clear Local Folder"),
				("PruneResources", "Prune Local Resources"),
			],
			"Edit": [
				("Copy", "Copy"),
				("Paste", "Paste"),
			],
			"Help": [
				("About", "About"),
				("LogFile", "Log File"),
			],
		}
	
	
	
	# implement update_[name] and on_[name] for each action
	'''
	def update_[name](self):
		
		return dict(
			caption = "Caption",
			icon = "icon.svg",
			shortcut = "Ctrl+S",
			help = "Tool tip",
			combo: list,
			checkable = True,
			checked = True,
			enabled = True,
		)
	
	def on_[name](self, state):
		
		pass
	'''
	
	def update_Connect(self):
		
		return dict(
			caption = "Connect",
			icon = "connect.svg",
			help = "Connect to Database",
			checkable = False,
			enabled = True,
		)
	
	def on_Connect(self, state):
		
		self.cmain.cdialogs.open("Connect")
	
	
	def update_Save(self):
		
		return dict(
			caption = "Save",
			icon = "save.svg",
			help = "Save",
			checkable = False,
			enabled = not self.cmain.cmodel.is_saved(),
		)
	
	def on_Save(self, state):
		
		if self.cmain.cmodel.can_save():
			self.cmain.cmodel.save()
		else:
			self.on_SaveAsFile(True)
	
	def on_SaveAsFile(self, state):
		
		path, format = self.cmain.cview.get_save_path("Save Database As", "Pickle (*.pickle);;JSON (*.json)")
		if not path:
			return
		self.cmain.cview.set_recent_dir(path)
		self.cmain.cmodel.save(path = path)
		url = as_url(path)
		self.cmain.cdialogs.open("ConfirmLoad", url)
	
	
	def update_SaveAsPostgres(self):
		
		return dict(
			help = "Save As PostgreSQL Database",
			checkable = False,
			enabled = True,
		)
	
	def on_SaveAsPostgres(self, state):
		
		self.cmain.cdialogs.open("SaveAsPostgres")
	
	
	def update_AutoBackup(self):
		
		return dict(
			help = "Backup database after every save",
			checkable = True,
			checked = self.cmain.cmodel.has_auto_backup(),
			enabled = True,
		)
	
	def on_AutoBackup(self, state):
		
		self.cmain.cmodel.set_auto_backup(state)
	
	
	def update_ImportDeposit(self):
		
		return dict(
			icon = "import.svg",
			help = "Import Deposit Database",
			checkable = False,
			enabled = True,
		)
	
	def on_ImportDeposit(self, state):
		
		self.cmain.cdialogs.open("ImportStoreSource")
	
	
	def update_ExportDeposit(self):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		return dict(
			icon = "export_deposit.svg",
			help = "Export to Deposit Database",
			checkable = False,
			enabled = isinstance(frame, QueryFrame) or (len(self.cmain.get_selected_objects()) > 0),
		)
	
	def on_ExportDeposit(self, state):
		
		objects = self.cmain.get_selected_objects()
		if not objects:
			frame = self.cmain.cmdiarea.get_current_frame()
			if isinstance(frame, QueryFrame):
				objects = set()
				for row in range(frame.get_row_count()):
					obj_id = frame.get_item(row, 0).obj_id_row
					if obj_id is not None:
						objects.add(self.cmain.cmodel.get_object(obj_id))
		if not objects:
			return
		
		store = self.cmain.cmodel.get_subgraph(objects)
		
		path, format = self.cmain.cview.get_save_path("Save Database As", "Pickle (*.pickle);;JSON (*.json)")
		if not path:
			return
		self.cmain.cview.set_recent_dir(path)
		self.cmain.cview.progress.show("Saving")
		store.save(path = path, progress = self.cmain.cview.progress)
		self.cmain.cview.progress.stop()
		url = as_url(path)
		self.cmain.cdialogs.open("ConfirmLoad", url)
	
	
	def update_SetLocalFolder(self):
		
		return dict(
			caption = "Set Local Folder",
			icon = None,
			help = "Set Local Folder",
			checkable = False,
			enabled = True,
		)
	
	def on_SetLocalFolder(self, state):
		
		folder = self.cmain.cview.get_existing_folder("Select Local Folder")
		if folder:
			self.cmain.cmodel.set_local_folder(folder)
	
	def update_ClearLocalFolder(self):
		
		return dict(
			caption = "Clear Local Folder",
			icon = "",
			help = "Clear Local Folder",
			checkable = False,
			enabled = self.cmain.cmodel.has_local_folder(),
		)
	
	def on_ClearLocalFolder(self, state):
		
		self.cmain.cmodel.set_local_folder(None)
	
	def update_PruneResources(self):
		
		return dict(
			caption = "Prune Local Resources",
			icon = "",
			help = "Prune Local Resources",
			checkable = False,
			enabled = (self.cmain.cmodel.get_folder() is not None),
		)
	
	def on_PruneResources(self, state):
		
		if self.cmain.cview.show_question(
			"Prune Local Resources",
			"Are you sure you want to delete all local resources not used in this database?"
		):
			self.cmain.cmodel.prune_resources()
	
	
	def update_AddRelation(self):
		
		return dict(
			icon = "link.svg",
			help = "Add Relation",
			checkable = False,
			enabled = len(self.cmain.get_selected_objects()) + len(self.cmain.get_selected_classes()) > 0,
		)
			
	def on_AddRelation(self, state):
		
		classes = self.cmain.get_selected_classes()
		if classes:
			self.cmain.cdialogs.open("AddRelation", list(classes), self._relation_label)
			return
		
		objects = self.cmain.get_selected_objects()
		if objects:
			self.cmain.cdialogs.open("AddRelation", list(objects), self._relation_label)
			return
	
	
	def update_RelationName(self):
		
		return dict(
			combo = natsorted(list(self.cmain.cmodel.get_relation_labels())),
			enabled = len(self.cmain.get_selected_objects()) + len(self.cmain.get_selected_classes()) > 0,
		)
	
	def on_RelationName(self, text):
		
		self._relation_label = text
	
	
	def update_RemoveRelation(self):
		
		return dict(
			icon = "unlink.svg",
			help = "Remove Relation",
			checkable = False,
			enabled = len(self.cmain.get_selected_relations()) > 0,
		)
	
	def on_RemoveRelation(self, state):
		
		relations = self.cmain.get_selected_relations()
		if relations:
			self.cmain.cdialogs.open("DelRelation", relations)
	
	
	def update_ClassGraph(self):
		
		return dict(
			icon = "classes_graph.svg",
			help = "Show Class Relations",
			checkable = False,
			enabled = True,
		)
	
	def on_ClassGraph(self, state):
		
		self.cmain.cmdiarea.add_class_graph()
	
	
	def update_FieldCalculator(self):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		return dict(
			icon = "calculator.svg",
			help = "Field Calculator",
			checkable = False,
			enabled = isinstance(frame, QueryFrame),
		)
	
	def on_FieldCalculator(self, state):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		if not isinstance(frame, QueryFrame):
			return
		rows = {}
		for row in range(frame.get_row_count()):
			obj_id = frame.get_item(row, 0).obj_id_row
			if obj_id is None:
				continue
			rows[obj_id] = {}
			for col in range(frame.get_column_count()):
				item = frame.get_item(row, col)
				rows[obj_id][(item.class_name, item.descriptor_name)] = item.value
		descriptor_name = None
		items = self.cmain.get_selected_queryitems()
		if items:
			descriptor_name = list(items)[0].descriptor_name
		if rows:
			self.cmain.cdialogs.open("FieldCalculator", rows, descriptor_name)
	
	
	def update_MergeRows(self):
		
		items = self.cmain.get_selected_queryitems()
		objects = set([item.obj_id_row for item in items])
		return dict(
			icon = "merge_objects.svg",
			help = "Merge Rows",
			checkable = False,
			enabled = len(objects) > 1,
		)
	
	def on_MergeRows(self, state):
		
		items = sorted(self.cmain.get_selected_queryitems(), key = lambda item: item.row)
		objects = []
		for item in items:
			if item.obj_id_row not in objects:
				objects.append(item.obj_id_row)
		if objects:
			self.cmain.cmodel.merge_objects(objects)
	
	
	def update_MergeIdentical(self):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		return dict(
			icon = "remove_duplicate_objects.svg",
			help = "Merge Identical Rows",
			checkable = False,
			enabled = isinstance(frame, QueryFrame),
		)
	
	def on_MergeIdentical(self, state):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		if not isinstance(frame, QueryFrame):
			return
		objects = set()
		for row in range(frame.get_row_count()):
			obj_id = frame.get_item(row, 0).obj_id_row
			if obj_id is None:
				continue
			objects.add(obj_id)
		if not objects:
			return
		if not self.cmain.cview.show_question(
			"Merge Objects", 
			"Are you sure you want to merge all Objects with identical Descriptors?"
		):
			return
		self.cmain.cmodel.merge_identical(objects)
		
	
	def update_Duplicate(self):
		
		items = self.cmain.get_selected_queryitems()
		return dict(
			icon = "split_objects.svg",
			help = "Duplicate Row",
			checkable = False,
			enabled = len(items) > 0,
		)
	
	def on_Duplicate(self, state):
		
		items = self.cmain.get_selected_queryitems()
		objects = set([item.obj_id_row for item in items])
		if objects:
			self.cmain.cmodel.duplicate(objects)
	
	
	def update_LoadExternal(self):
		
		return dict(
			icon = "load_external.svg",
			help = "Load External Data",
			checkable = False,
			enabled = True,
		)
	
	def on_LoadExternal(self, state):
		
		formats = [
			"Excel 2007+ Workbook (*.xlsx)",
			"Comma-separated Values (*.csv)",
			"ESRI Shapefile (*.shp)",
		]
		path, format = self.cmain.cview.get_load_path("Load External Data", ";;".join(formats))
		if not path:
			return
		self.cmain.cview.set_recent_dir(path)
		self.cmain.cmdiarea.add_external(as_url(path))
	
	
	def update_ImportExternal(self):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		return dict(
			icon = "import_external.svg",
			help = "Import Data",
			checkable = False,
			enabled = isinstance(frame, ExternalFrame),
		)
	
	def on_ImportExternal(self, state):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		if isinstance(frame, ExternalFrame):
			self.cmain.cdialogs.open("ImportExternal", frame)
			return
	
	
	def update_ExportExternal(self):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		return dict(
			icon = "export_external.svg",
			help = "Export Data",
			checkable = False,
			enabled = isinstance(frame, QueryFrame),
		)
	
	def on_ExportExternal(self, state):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		if not isinstance(frame, QueryFrame):
			return
		formats = [
			("Excel 2007+ Workbook (*.xlsx)", "XLSX"),
			("Comma-separated Values (*.csv)", "CSV"),
			("ESRI Shapefile (*.shp)", "SHP"),
		]
		path, format = self.cmain.cview.get_save_path(
			"Save Data As", ";;".join([format[0] for format in formats])
		)
		if not path:
			return
		if not format in dict(formats):
			return
		self.cmain.cview.set_recent_dir(path)
		source = dict(formats)[format]
		if not hasattr(Externalsource, source):
			raise Exception("Export format not supported: %s" % (source))
		externalsource = getattr(Externalsource, source)()
		ret = externalsource.save(frame.get_header, frame.get_item, 
			frame.get_row_count(), frame.get_column_count(),
			path = path
		)
		self.cmain.cview.show_information("Export Successful", "Exported to: %s" % (path))
	
	
	def update_Copy(self):
		
		items = self.cmain.get_selected_queryitems()
		return dict(
			caption = "Copy",
			icon = "copy.svg",
			shortcut = "Ctrl+C",
			help = "Copy to Clipboard",
			enabled = len(items) > 0,
		)
	
	def on_Copy(self, state):
		
		items = self.cmain.get_selected_queryitems()
		if not items:
			return
		data = defaultdict(dict)
		columns = set()
		for item in items:
			value = value_to_str(item.value)
			if value is None:
				continue
			data[item.row][item.column] = value
			columns.add(item.column)
		if (not data) or (not columns):
			return
		row_min = min(data.keys())
		row_max = max(data.keys())
		col_min = min(columns)
		col_max = max(columns)
		rows = []
		for row in range(row_min, row_max + 1):
			rows.append("\t".join([
				data.get(row, {}).get(col, "") for col in range(col_min, col_max + 1)
			]))
		rows = "\n".join(rows)
		data = QtCore.QMimeData()
		data.setData("text/plain", bytes(rows, "utf-8"))
		QtWidgets.QApplication.clipboard().setMimeData(data)
	
	def update_Paste(self):
		
		items = self.cmain.get_selected_queryitems()
		return dict(
			caption = "Paste",
			icon = "paste.svg",
			shortcut = "Ctrl+V",
			help = "Paste from Clipboard",
			enabled = len(items) == 1,
		)
	
	def on_Paste(self, state):
		
		frame = self.cmain.cmdiarea.get_current_frame()
		items = self.cmain.get_selected_queryitems()
		if len(items) != 1:
			return
		item = list(items)[0]
		if (item.obj_id is None) or (item.descriptor_name is None):
			return
		obj = self.cmain.cmodel.get_object(item.obj_id)
		
		cb = QtWidgets.QApplication.clipboard()
		mimedata = cb.mimeData()
		
		if mimedata.hasUrls():
			url = str(mimedata.urls()[0].toString())
			obj.set_resource_descriptor(item.descriptor_name, url)
			return
		
		if mimedata.hasImage():
			filename = []
			if item.class_name is not None:
				filename.append(item.class_name)
			filename.append(item.descriptor_name)
			filename.append(str(item.obj_id))
			filename = sanitize_filename("_".join(filename) + ".png")
			pixmap = QtGui.QPixmap(mimedata.imageData())
			path = os.path.join(get_temp_path(), filename)
			pixmap.save(path)
			obj.set_resource_descriptor(item.descriptor_name, as_url(path))
			return
		
		if mimedata.hasText():
			obj.set_descriptor(item.descriptor_name, mimedata.text())
			return
		
	
	def on_About(self, state):
		
		self.cmain.cdialogs.open("About")
	
	def on_LogFile(self, state):
		
		self.cmain.open_in_external(self.cmain.cview.get_logging_path())

