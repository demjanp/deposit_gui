from deposit_gui.view.vusertools_elements.user_elements.query import (Query)

from PySide6 import (QtWidgets, QtCore)

class EditorQuery(QtWidgets.QDialog):
	
	signal_add_tool = QtCore.Signal(object)			# query
	signal_update_tool = QtCore.Signal(str, object)	# label, query
	
	def __init__(self, vusertools, query_tool):
		
		QtWidgets.QDialog.__init__(self, vusertools.vmain)
		
		self._vusertools = vusertools
		self.query_tool = query_tool
		
		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
		self.setWindowTitle("Edit Query Tool")
		
		self.setMinimumWidth(600)
		self.setModal(True)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		
		self.title_edit = QtWidgets.QLineEdit()
		self.query_edit = QtWidgets.QPlainTextEdit()
		form = QtWidgets.QFrame()
		form_layout = QtWidgets.QFormLayout()
		form.setLayout(form_layout)
		form.layout().setContentsMargins(0, 0, 0, 0)
		form.layout().addRow("Title:", self.title_edit)
		form.layout().addRow("Query:", self.query_edit)
		self.layout().addWidget(form)
		
		self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel, QtCore.Qt.Orientation.Horizontal)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		self.layout().addWidget(self.buttonBox)
		
		self.finished.connect(self.on_finished)
		
		if self.query_tool is not None:
			self.title_edit.setText(self.query_tool.label)
			self.query_edit.setPlainText(self.query_tool.value)
	
	def save(self):
		
		title = self.title_edit.text()
		querystr = self.query_edit.toPlainText()
		if title and querystr:
			query = Query(title, querystr, self._vusertools)
			if self.query_tool is None:
				self.signal_add_tool.emit(query)
			else:
				self.signal_update_tool.emit(self.query_tool.label, query)
	
	@QtCore.Slot(object)
	def on_finished(self, code):
		
		if code == QtWidgets.QDialog.DialogCode.Accepted:
			self.save()