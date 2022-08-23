from PySide2 import (QtWidgets, QtCore, QtGui)

class DToolBar(QtCore.QObject):
	
	signal_triggered = QtCore.Signal(str)
	signal_combo_changed = QtCore.Signal(str, str)
	
	def __init__(self, view):
		
		QtCore.QObject.__init__(self)
		
		self.view = view
		
		self.toolbars = {} # {name: QToolBar, ...}
		self.actions = {}  # {name: QAction, ...}
	
	def populate(self, tools):
		# tools = {toolbar: [(name, caption), None, ...], ...}; if None: add separator
		
		for toolbar_name in tools:
			self.toolbars[toolbar_name] = self.view.addToolBar(toolbar_name)
			self.toolbars[toolbar_name].setIconSize(QtCore.QSize(36,36))
			for name in tools[toolbar_name]:
				if name is None:
					self.toolbars[toolbar_name].addSeparator()
				else:
					name, caption = name
					self.actions[name] = QtWidgets.QAction(caption)
					self.actions[name].setData(name)
					self.actions[name]._toolbar_name = toolbar_name
					self.toolbars[toolbar_name].addAction(self.actions[name])
			self.toolbars[toolbar_name].actionTriggered.connect(self.on_triggered)
	
	def get_names(self):
		
		return list(self.actions.keys())
	
	def update_tool(self, name, data, child_window = False, clear_combo_text = False):
		'''
		data = {
			caption: str,
			icon: str,
			shortcut: str,
			help: str,
			combo: list,
			editable: bool,
			checkable: bool,
			checked: bool,
			enabled: bool,
		}
		child_window = True if toolbar is in a child window
		'''
		
		if name not in self.actions:
			return
		if "combo" in data:
			items = data["combo"]
			if isinstance(items, list):
				if not isinstance(self.actions[name], ComboAction):
					toolbar_name = self.actions[name]._toolbar_name
					caption = self.actions[name].text()
					action = ComboAction(name, toolbar_name, self.view)
					action.currentTextChanged.connect(
						lambda text: self.on_combo_changed(name, text)
					)
					if caption:
						self.toolbars[toolbar_name].insertWidget(
							self.actions[name], QtWidgets.QLabel(caption)
						)
					self.toolbars[toolbar_name].insertWidget(self.actions[name], action)
					self.toolbars[toolbar_name].removeAction(self.actions[name])
					self.actions[name] = action
				text = self.actions[name].currentText()
				self.actions[name].blockSignals(True)
				self.actions[name].clear()
				self.actions[name].addItems(items)
				i = self.actions[name].findText(
					text, flags = QtCore.Qt.MatchExactly|QtCore.Qt.MatchCaseSensitive
				)
				if i > -1:
					self.actions[name].setCurrentIndex(i)
				elif (text and not clear_combo_text):
					self.actions[name].setCurrentText(text)
				if self.actions[name].currentText() != text:
					self.on_combo_changed(name, self.actions[name].currentText())
				if "editable" in data:
					self.actions[name].setEditable(data["editable"])
				self.actions[name].adjustSize()
				self.actions[name].blockSignals(False)
		if "caption" in data:
			self.actions[name].setText(data["caption"])
		if ("icon" in data) and data["icon"]:
			self.actions[name].setIcon(self.view.get_icon(data["icon"]))
		if "shortcut" in data:
			self.actions[name].setShortcut(QtGui.QKeySequence(data["shortcut"]))
			if child_window:
				self.actions[name].setShortcutContext(QtCore.Qt.WindowShortcut)
			else:
				self.actions[name].setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)
		if "help" in data:
			self.actions[name].setToolTip(data["help"])
		if "checkable" in data:
			self.actions[name].setCheckable(data["checkable"])
		if "checked" in data:
			self.actions[name].setChecked(data["checked"])
		if "enabled" in data:
			self.actions[name].setEnabled(data["enabled"])
	
	def set_toolbar_visible(self, name, state):
		
		if name not in self.toolbars:
			return
		self.toolbars[name].setVisible(state)
	
	def get_state(self, name):
		
		if name not in self.actions:
			return False
		return self.actions[name].isChecked()
	
	def get_combo_value(self, name):
		
		if (name in self.actions) and isinstance(self.actions[name], ComboAction):
			return self.actions[name].currentText()
	
	def set_combo_value(self, name, text):
		
		if (name in self.actions) and isinstance(self.actions[name], ComboAction):
			self.actions[name].blockSignals(True)
			self.actions[name].setCurrentText(text)
			self.actions[name].blockSignals(False)
	
	@QtCore.Slot(QtWidgets.QAction)
	def on_triggered(self, action):
		
		self.signal_triggered.emit(str(action.data()))
	
	@QtCore.Slot(str, str)
	def on_combo_changed(self, name, text):
		
		self.signal_combo_changed.emit(name, text)
	
class ComboAction(QtWidgets.QComboBox):
	
	def __init__(self, name, toolbar_name, view):
		
		QtWidgets.QComboBox.__init__(self, view)
		
		self._name = name
		self._toolbar_name = toolbar_name
		
		self.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
		self.setEditable(True)

