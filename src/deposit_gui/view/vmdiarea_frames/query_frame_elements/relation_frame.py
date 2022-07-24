from deposit_gui.view.vmdiarea_frames.abstract_mdiarea_frame import AbstractMDIAreaFrame
from PySide2 import (QtWidgets, QtCore, QtGui)
from natsort import (natsorted)
from urllib.parse import (urlencode, parse_qsl)

class RelationFrame(QtWidgets.QFrame):
	
	signal_object_link = QtCore.Signal(int)		# obj_id
	signal_class_link = QtCore.Signal(str)		# class_name
	signal_relation_link = QtCore.Signal(int, str, str)	# obj_id, rel_label, class_name
	
	def __init__(self):
		
		QtWidgets.QFrame.__init__(self)
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		self.setStyleSheet('''
			QFrame {
				background-color: white;
			}
		''')
		
		form_header = QtWidgets.QWidget()
		form_header.setLayout(QtWidgets.QFormLayout())
		form_header.layout().setContentsMargins(0, 0, 0, 0)
		self.label_obj_id = QtWidgets.QLabel("None")
		self.label_obj_id.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
		self.label_obj_id.linkActivated.connect(self.on_object_link)
		self.label_classes = QtWidgets.QLabel("None")
		self.label_classes.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
		self.label_classes.linkActivated.connect(self.on_class_link)
		form_header.layout().addRow("<b>Object ID:</b>", self.label_obj_id)
		form_header.layout().addRow("<b>Classes:</b>", self.label_classes)
		
		self.list_related = QtWidgets.QWidget()
		self.list_related.setLayout(QtWidgets.QVBoxLayout())
		self.list_related.layout().setContentsMargins(0, 0, 0, 0)
		
		self.layout().addWidget(form_header)
		self.layout().addWidget(QtWidgets.QLabel("<b>Related:</b>"))
		self.layout().addWidget(self.list_related)
		self.layout().addStretch()
		
	def populate(self, obj):
		
		for i in reversed(range(self.list_related.layout().count())):
			self.list_related.layout().itemAt(i).widget().deleteLater()
		
		if obj is None:
			self.label_obj_id.setText("None")
			self.label_classes.setText("None")
			return
		
		class_names = [cls.name for cls in obj.get_classes(ordered = True)]
		
		self.label_obj_id.setText("<a style=\"text-decoration:none;\" href=\"%s\">%d</a>" % (urlencode({"obj_id": obj.id}), obj.id))
		self.label_classes.setText(", ".join([
			"<a style=\"text-decoration:none;\" href=\"%s\">%s</a>" % (urlencode({"name": name}), name) for name in class_names
		]))
		relations = set()
		for obj_tgt, label in obj.get_relations():
			for cls in obj_tgt.get_classes():
				relations.add((label, cls.name))
		relations = natsorted(list(relations))
		for label, name in relations:
			label = QtWidgets.QLabel("<a style=\"text-decoration:none;\" href=\"%s\">%s.%s</a>" % (urlencode({"obj_id": obj.id, "label": label, "name": name}), label, name))
			label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
			label.linkActivated.connect(self.on_relation_link)
			self.list_related.layout().addWidget(label)
	
	@QtCore.Slot(str)
	def on_object_link(self, text):
		
		obj_id = int(parse_qsl(text)[0][1])
		self.signal_object_link.emit(obj_id)
	
	@QtCore.Slot(str)
	def on_class_link(self, text):
		
		name = parse_qsl(text)[0][1]
		self.signal_class_link.emit(name)
	
	@QtCore.Slot(str)
	def on_relation_link(self, text):
		
		data = dict(parse_qsl(text))
		obj_id = int(data["obj_id"])
		label = data["label"]
		name = data["name"]
		self.signal_relation_link.emit(obj_id, label, name)

