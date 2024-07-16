from deposit_gui.dgui.dcdialogs import DCDialogs
from deposit_gui.dgui.dsave_as_postgres_frame import DSaveAsPostgresFrame
from deposit_gui.dialogs.dialog_connect import DialogConnect
from deposit_gui.dialogs.dialog_import_source import DialogImportSource
from deposit_gui.dialogs.dialog_import_store import DialogImportStore
from deposit_gui.dialogs.dialog_import_external import DialogImportExternal
from deposit_gui.dialogs.dialog_add_relation import DialogAddRelation
from deposit_gui.dialogs.dialog_about import DialogAbout
from deposit import Store

from PySide6 import (QtWidgets, QtCore, QtGui)
from natsort import (natsorted)
import os

class CDialogs(DCDialogs):
	
	def __init__(self, cmain, cview):
		
		DCDialogs.__init__(self, cmain, cview)
		
		self.view = cview._view
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	@QtCore.Slot()
	def on_clear_recent(self):
		
		self.view.clear_recent_connections()
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	
	
	# ---- Dialogs
	# ------------------------------------------------------------------------
	'''
	open(name, *args, **kwargs)
	
	Implement set_up_[name], process_[name] and cancel_[name] for each dialog:
	
	def set_up_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		dialog = QtWidgets.QDialog
		
		dialog.set_title(name)
		dialog.set_frame(frame = QtWidget)
		dialog.get_frame()
		dialog.set_button_box(ok: bool, cancel: bool): set if OK and Cancel buttons are visible
		
	def process_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		process dialog after OK has been clicked
	
	def cancel_[name](self, dialog, *args, **kwargs):
		
		args and kwargs are passed from DCDialogs.open(name, *args, **kwargs)
		
		handle dialog after cancel has been clicked
	'''
	
	def set_up_Connect(self, dialog, *args, **kwargs):
		
		connect_frame = DialogConnect(dialog)
		connect_frame.set_recent_dir(self.view.get_recent_dir())
		connect_frame.set_recent_connections(self.view.get_recent_connections())
		connect_frame.signal_clear_recent.connect(self.on_clear_recent)
		
	def process_Connect(self, dialog, *args, **kwargs):
		
		self.cmain.cmodel.load(**dialog.get_data())
	
	def cancel_Connect(self, dialog, *args, **kwargs):
		
		datasource = self.cmain.cmodel.get_datasource()
		if not datasource.is_valid():
			self.cmain.cmodel.load(datasource = "Memory")
	
	
	def set_up_SaveAsPostgres(self, dialog, *args, **kwargs):
		
		frame = DSaveAsPostgresFrame(dialog)
		frame.set_recent_connections(self.view.get_recent_connections())
	
	def process_SaveAsPostgres(self, dialog, *args, **kwargs):
		
		data = dialog.get_data()
		datasource = data["datasource"]
		self.cmain.cmodel.set_local_folder(datasource.get_local_folder())
		self.cmain.cmodel.save(**data)
		
		reply = QtWidgets.QMessageBox.question(self.cmain.cview._view, 
			"Load Database?", 
			"Load database from <b>%s</b>" % (datasource.get_name()),
		)
		if reply == QtWidgets.QMessageBox.StandardButton.Yes:
			self.cmain.cmodel.load(**data)
	
	
	def set_up_ImportStoreSource(self, dialog):
		
		connect_frame = DialogImportSource(dialog)
		connect_frame.set_recent_dir(self.view.get_recent_dir())
		connect_frame.set_recent_connections(self.view.get_recent_connections())
	
	def process_ImportStoreSource(self, dialog):
		
		self.cmain.cview.progress.show("Loading")
		kwargs = dialog.get_data()
		store = Store(keep_temp = True)
		store.load(progress = self.cmain.cview.progress, **kwargs)
		self.cmain.cmodel.update_recent(kwargs)
		self.cmain.cview.progress.stop()
		if not store.get_objects():
			return
		self.open("ImportStore", store)
	
	def set_up_ImportStore(self, dialog, store):
		
		classes = store.get_class_names(ordered = True)
		descriptors = store.get_descriptor_names()
		classes = [name for name in classes if name not in descriptors]
		frame = DialogImportStore(dialog, store.get_objects(), classes)
		dialog.set_frame(frame)
	
	def process_ImportStore(self, dialog, store):
		
		unique = dialog.get_frame().get_unique()
		match_empty = dialog.get_frame().get_match_empty()
		self.cmain.cmodel.import_store(store, unique, match_empty)
	
	
	def set_up_ImportExternal(self, dialog, external_frame):
		
		targets = external_frame.get_targets()  # {column_idx: (class_name, descriptor_name), ...}
		classes = set()
		for class_name, _ in targets.values():
			cls = self.cmain.cmodel.get_class(class_name)
			if cls:
				classes.add(cls)
		relations = set()
		for cls in classes:
			for cls2, label in cls.get_relations():
				if label.startswith("~"):
					continue
				if cls2 not in classes:
					continue
				relations.add((cls.name, label, cls2.name))
		classes = natsorted([cls.name for cls in classes])
		relations = natsorted(relations)
		
		n_rows = external_frame.get_row_count()
		frame = DialogImportExternal(dialog, n_rows, classes, relations)
		dialog.set_frame(frame)
	
	def process_ImportExternal(self, dialog, external_frame):
		
		frame = dialog.get_frame()
		unique = frame.get_unique()
		relations = frame.get_relations()
		match_empty = frame.get_match_empty()
		n_rows = external_frame.get_row_count()
		targets = external_frame.get_targets()
		n_imported = self.cmain.cmodel.import_data(external_frame.get_data, n_rows, targets, relations, unique, match_empty)
		self.cmain.cview.show_information("Import Successful", "Imported %d Objects" % (n_imported))
	
	
	def set_up_ConfirmLoad(self, dialog, url):
		
		dialog.set_title("Load Database?")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.layout().addWidget(QtWidgets.QLabel("Load database from <b>%s</b>?" % (os.path.split(url)[-1])))
		
		dialog.set_frame(frame)
	
	def process_ConfirmLoad(self, dialog, url):
		
		self.cmain.cmodel.load(url = url)
	
	
	def set_up_AddClass(self, dialog, parent_cls):
		
		dialog.set_title("Add Class")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.name_edit = QtWidgets.QLineEdit()
		frame.name_edit.setPlaceholderText("Class name")
		caption = ""
		if parent_cls is not None:
			caption = "As subclass of %s" % (parent_cls.name)
		frame.as_subclass = QtWidgets.QCheckBox(caption)
		frame.layout().addWidget(frame.name_edit)
		if parent_cls is not None:
			frame.layout().addWidget(frame.as_subclass)
			
		dialog.set_frame(frame)
	
	def process_AddClass(self, dialog, parent_cls):
		
		frame = dialog.get_frame()
		name = frame.name_edit.text()
		as_subclass = frame.as_subclass.isChecked()
		if not name:
			return
		cls = self.cmain.cmodel.add_class(name)
		if as_subclass:
			parent_cls.add_subclass(cls)
	
	
	def set_up_AddDescriptor(self, dialog, cls):
		
		dialog.set_title("Add Descriptor")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.name_edit = QtWidgets.QLineEdit()
		frame.name_edit.setPlaceholderText("Descriptor name")
		frame.layout().addWidget(frame.name_edit)
		
		dialog.set_frame(frame)
	
	def process_AddDescriptor(self, dialog, cls):
		
		frame = dialog.get_frame()
		name = frame.name_edit.text()
		if not name:
			return
		self.cmain.cmodel.get_class(cls).set_descriptor(name)
	
	
	def set_up_DelDescriptor(self, dialog, descr, cls):
		
		dialog.set_title("Remove Descriptor")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove descriptor <b>%s</b> from class <b>%s</b>?" % (descr.name, cls.name)
		))
		frame.class_only = QtWidgets.QCheckBox("Only remove class descriptor (not from objects)")
		frame.layout().addWidget(frame.class_only)
		
		dialog.set_frame(frame)
	
	def process_DelDescriptor(self, dialog, descr, cls):
		
		frame = dialog.get_frame()
		class_only = frame.class_only.isChecked()
		self.cmain.cmodel.del_class_descriptor(descr, cls, class_only)
	
	
	def set_up_RenameClass(self, dialog, cls, is_descriptor, parent_cls):
		
		dialog.set_title("Rename Descriptor" if is_descriptor else "Rename Class")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.name_edit = QtWidgets.QLineEdit()
		frame.name_edit.setText(cls.name)
		caption = ""
		if is_descriptor and (parent_cls is not None):
			caption = "Only rename Descriptor of class %s" % (parent_cls.name)
		frame.parent_only = QtWidgets.QCheckBox(caption)
		frame.layout().addWidget(frame.name_edit)
		if is_descriptor and (parent_cls is not None):
			frame.layout().addWidget(frame.parent_only)
			
		dialog.set_frame(frame)
	
	def process_RenameClass(self, dialog, cls, is_descriptor, parent_cls):
		
		frame = dialog.get_frame()
		name = frame.name_edit.text()
		parent_only = frame.parent_only.isChecked()
		if not name:
			return
		if parent_only:
			self.cmain.cmodel.rename_class_descriptor(cls, parent_cls, name)
		else:
			self.cmain.cmodel.rename_class(cls, name)
	
	
	def set_up_DelClass(self, dialog, classes):
		
		dialog.set_title("Remove Class")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		names = [cls.name for cls in classes]
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove the following class%s?" % ("es" if (len(names) > 1) else "")
		))
		frame.layout().addWidget(QtWidgets.QLabel("<b>%s</b>" % ", ".join(names)))
		frame.superclasses = set()
		for cls in classes:
			frame.superclasses.update(set(cls.get_superclasses()))
		frame.del_superclasses = QtWidgets.QCheckBox("Only remove from superclasses?")
		if frame.superclasses:
			frame.layout().addWidget(frame.del_superclasses)
			
		dialog.set_frame(frame)
	
	def process_DelClass(self, dialog, classes):
		
		frame = dialog.get_frame()
		del_superclasses = frame.del_superclasses.isChecked()
		if del_superclasses:
			for supcls in frame.superclasses:
				for cls in classes:
					supcls.del_subclass(cls)
		else:
			for cls in classes:
				self.cmain.cmodel.del_class(cls)
	
	
	def set_up_AddSavedQuery(self, dialog):
		
		querystr = self.cmain.cquerytoolbar.get_query_text()
		
		dialog.set_title("Add Query")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.title_edit = QtWidgets.QLineEdit()
		frame.title_edit.setPlaceholderText("Title")
		frame.querystr_edit = QtWidgets.QPlainTextEdit()
		if querystr:
			frame.querystr_edit.setPlainText(querystr)
		else:
			frame.querystr_edit.setPlaceholderText("Query String")
		frame.layout().addWidget(frame.title_edit)
		frame.layout().addWidget(frame.querystr_edit)
		
		dialog.set_frame(frame)
	
	def process_AddSavedQuery(self, dialog):
		
		frame = dialog.get_frame()
		title = frame.title_edit.text()
		querystr = frame.querystr_edit.toPlainText()
		if title and querystr:
			self.cmain.cmodel.add_saved_query(title, querystr)
	
	
	def set_up_EditSavedQuery(self, dialog, title):
		
		querystr = self.cmain.cmodel.get_saved_query(title)
		
		dialog.set_title("Edit Query")
		dialog.setModal(True)
		dialog.set_button_box(True, True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		frame.title_edit = QtWidgets.QLineEdit()
		frame.title_edit.setText(title)
		frame.querystr_edit = QtWidgets.QPlainTextEdit()
		frame.querystr_edit.setPlainText(querystr)
		frame.layout().addWidget(frame.title_edit)
		frame.layout().addWidget(frame.querystr_edit)
		
		dialog.set_frame(frame)
		
	
	def process_EditSavedQuery(self, dialog, title):
		
		frame = dialog.get_frame()
		title_new = frame.title_edit.text()
		querystr = frame.querystr_edit.toPlainText()
		if title_new and querystr:
			if title_new != title:
				self.cmain.cmodel.del_saved_query(title)
			self.cmain.cmodel.add_saved_query(title_new, querystr)
	
	def set_up_RemoveSavedQuery(self, dialog, titles):
		
		dialog.set_title("Remove %s" % ("Queries" if len(titles) > 1 else "Query"))
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove the following %s?" % ("queries" if len(titles) > 1 else "query")
		))
		frame.layout().addWidget(QtWidgets.QLabel("".join(["<p><b>%s</b></p>" % (title) for title in titles])))
		
		dialog.set_frame(frame)
	
	def process_RemoveSavedQuery(self, dialog, titles):
		
		for title in titles:
			self.cmain.cmodel.del_saved_query(title)
	
	
	def set_up_DelObjects(self, dialog, objects):
		
		dialog.set_title("Remove Object%s" % ("s" if len(objects) > 1 else ""))
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove the following object%s?" % ("s" if (len(objects) > 1) else "")
		))
		frame.layout().addWidget(QtWidgets.QLabel("<b>%s</b>" % ", ".join(sorted([str(obj.id) for obj in objects]))))
				
		dialog.set_frame(frame)
	
	def process_DelObjects(self, dialog, objects):
		
		self.cmain.cmodel.del_objects(objects)
	
	
	def set_up_AddClassToObjects(self, dialog, objects):
		
		dialog.set_title("Add to Class")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		
		classes = self.cmain.cmodel.get_class_names(ordered = True)
		descriptors = self.cmain.cmodel.get_descriptor_names()
		classes = [name for name in classes if name not in descriptors]
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		frame.class_combo = QtWidgets.QComboBox()
		frame.class_combo.addItems([""] + classes)
		frame.class_combo.setEditable(True)
		
		frame.layout().addWidget(QtWidgets.QLabel(
			"Add Object%s to Class:" % "s" if (len(objects) > 1) else "",
		))
		frame.layout().addWidget(frame.class_combo)
				
		dialog.set_frame(frame)
	
	def process_AddClassToObjects(self, dialog, objects):
		
		frame = dialog.get_frame()
		name = frame.class_combo.currentText().strip()
		if not name:
			return
		cls = self.cmain.cmodel.add_class(name)
		
		for obj in objects:
			cls.add_member(obj)
	
	
	def set_up_DelClassFromObjects(self, dialog, cls, objects):
		
		dialog.set_title("Remove from Class")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove the following object%s from Class %s?" % (
				"s" if (len(objects) > 1) else "",
				cls.name
			)
		))
		frame.layout().addWidget(QtWidgets.QLabel("<b>%s</b>" % ", ".join(sorted([str(obj.id) for obj in objects]))))
		
		dialog.set_frame(frame)
	
	def process_DelClassFromObjects(self, dialog, cls, objects):
		
		for obj in objects:
			cls.del_member(obj)
	
	
	def set_up_AddRelation(self, dialog, elements, label):
		
		is_class = (elements[0].__class__.__name__ == "DClass")
		dialog.set_frame(DialogAddRelation(dialog, self.cmain, elements, label, is_class))
	
	def process_AddRelation(self, dialog, elements, label):
		
		frame = dialog.get_frame()
		label = frame.get_label()
		targets = frame.get_targets()
		if (not label) or (not targets):
			return
		for src in elements:
			for tgt in targets:
				src.add_relation(tgt, label)
	
	
	def set_up_DelRelation(self, dialog, relations):
		
		dialog.set_title("Remove Relation%s" % ("s" if len(relations) > 1 else ""))
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(300)
		layout = QtWidgets.QVBoxLayout()
		frame.setLayout(layout)
		
		frame.layout().addWidget(QtWidgets.QLabel(
			"Remove the selected relation%s?" % ("s" if (len(relations) > 1) else "")
		))
		
		dialog.set_frame(frame)
	
	def process_DelRelation(self, dialog, relations):
		
		for src, tgt, label in relations:
			src.del_relation(tgt, label)
	
	
	def set_up_FieldCalculator(self, dialog, rows, descriptor_name):
		
		dialog.set_title("About Deposit")
		dialog.set_button_box(True, True)
		dialog.setModal(True)
		
		frame = QtWidgets.QFrame()
		frame.setMinimumWidth(600)
		layout = QtWidgets.QHBoxLayout()
		frame.setLayout(layout)
		frame.target_edit = QtWidgets.QLineEdit()
		if descriptor_name is None:
			frame.target_edit.setPlaceholderText("Descriptor name")
		else:
			frame.target_edit.setText(descriptor_name)
		frame.target_edit.setFixedWidth(100)
		frame.expr_edit = QtWidgets.QPlainTextEdit()
		frame.expr_edit.setPlaceholderText(
		'''Python expression e.g.:

Class1.Descr1 + [Class 1].[Descr 2]
Class1.Descr1.filename if isinstance(Class1.Descr1, DResource) else None
DGeometry('POINT(10 20)')
DGeometry('POINT', [10, 20], 4326)  # 4326 = SRID
DResource('C:/folder/' + Class1.Descr1.filename)
DDateTime('2022-07-20T19:31:00.729558')
		''')
		label = QtWidgets.QLabel("=")
		frame.layout().addWidget(frame.target_edit)
		frame.layout().addWidget(label)
		frame.layout().addWidget(frame.expr_edit)
		
		frame.layout().setAlignment(frame.target_edit, QtCore.Qt.AlignmentFlag.AlignTop)
		frame.layout().setAlignment(label, QtCore.Qt.AlignmentFlag.AlignTop)
		
		dialog.set_frame(frame)
	
	def process_FieldCalculator(self, dialog, rows, descriptor_name):
		
		frame = dialog.get_frame()
		target = frame.target_edit.text().strip()
		expr = frame.expr_edit.toPlainText().strip()
		if target and expr:
			self.cmain.cmodel.field_calculator(target, expr, rows)
	
	
	def set_up_About(self, dialog):
		
		dialog.set_title("About Deposit")
		dialog.set_button_box(True, False)
		dialog.setModal(True)
		dialog.set_frame(DialogAbout())

