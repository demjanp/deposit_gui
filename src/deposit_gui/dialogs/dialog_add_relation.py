from PySide6 import (QtWidgets, QtCore, QtGui)

class DialogAddRelation(QtWidgets.QFrame):
	
	def __init__(self, dialog, cmain, elements, label, is_class):
		
		QtWidgets.QFrame.__init__(self)
		
		self._dialog = dialog
		self._cmain = cmain
		self._elements = elements
		self._is_class = is_class
		self._targets = []
		
		self._dialog.set_title("Add %sRelation" % ("Class " if self._is_class else ""))
		self._dialog.setModal(False)
		self._dialog.set_button_box(True, True)
		self._dialog.set_enabled(False)
		
		self.setMinimumWidth(256)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		labels = QtWidgets.QWidget()
		labels_layout = QtWidgets.QHBoxLayout()
		labels.setLayout(labels_layout)
		self.label_source = QtWidgets.QLabel("")
		self.label_relation = QtWidgets.QLineEdit(label)
		if not label:
			self.label_relation.setPlaceholderText("Relation name")
		self.label_target = QtWidgets.QLabel("")
		labels.layout().addWidget(self.label_source)
		labels.layout().addWidget(self.label_relation)
		labels.layout().addWidget(self.label_target)
		self.layout().addWidget(labels)
		
		self._cmain.signal_selection_changed.connect(self.on_selection_changed)
		
		self.update()
	
	def update(self):
		
		source_txt = " \u2192 "
		target_txt = " \u2192 "
		if self._is_class:
			source_txt = "%s \u2192 " % (", ".join([cls.name for cls in self._elements]))
			if self._targets:
				target_txt = " \u2192 %s" % (", ".join([cls.name for cls in self._targets]))
		else:
			source_txt = "obj(%s) \u2192 " % (", ".join([str(obj_id) for obj_id in sorted([obj.id for obj in self._elements])]))
			if self._targets:
				target_txt = " \u2192 obj(%s)" % (", ".join([str(obj_id) for obj_id in sorted([obj.id for obj in self._targets])]))
		self.label_source.setText(source_txt)
		self.label_target.setText(target_txt)
		
		label = self.get_label()
		
		self._dialog.set_enabled((len(self._targets) > 0) and (label != ""))
	
	def get_label(self):
		
		return self.label_relation.text().strip()
	
	def get_targets(self):
		
		return self._targets
	
	@QtCore.Slot()
	def on_selection_changed(self):
		
		if self._is_class:
			self._targets = list(self._cmain.get_selected_classes())
		else:
			self._targets = list(self._cmain.get_selected_objects())
		
		self.update()

