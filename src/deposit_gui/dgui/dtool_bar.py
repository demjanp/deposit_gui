from PySide6 import (QtWidgets, QtCore, QtGui)
from collections import defaultdict

class DToolBar(QtCore.QObject):
	
	signal_triggered = QtCore.Signal(str)
	signal_combo_changed = QtCore.Signal(str, str)
	
	def __init__(self, view):
		
		QtCore.QObject.__init__(self)
		
		self.view = view
		
		self.toolbars = {} # {name: QToolBar, ...}
		self.actions = defaultdict(list)  # {name: [QAction, ...], ...}
	
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
					self.actions[name].append(QtGui.QAction(caption))
					self.actions[name][-1].setData(name)
					self.actions[name][-1]._toolbar_name = toolbar_name
					self.toolbars[toolbar_name].addAction(self.actions[name][-1])
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
				collect = []
				for action in self.actions[name]:
					if not isinstance(action, ComboAction):
						toolbar_name = action._toolbar_name
						caption = action.text()
						action_ = ComboAction(name, toolbar_name, self.view)
						action_.currentTextChanged.connect(
							lambda text: self.on_combo_changed(name, text)
						)
						if caption:
							self.toolbars[toolbar_name].insertWidget(
								action, QtWidgets.QLabel(caption)
							)
						self.toolbars[toolbar_name].insertWidget(action, action_)
						self.toolbars[toolbar_name].removeAction(action)
						collect.append(action_)
						action = action_
					text = action.currentText()
					action.blockSignals(True)
					action.clear()
					action.addItems(items)
					i = action.findText(
						text, flags = QtCore.Qt.MatchFlag.MatchExactly|QtCore.Qt.MatchFlag.MatchCaseSensitive
					)
					if i > -1:
						action.setCurrentIndex(i)
					elif (text and not clear_combo_text):
						action.setCurrentText(text)
					if action.currentText() != text:
						self.on_combo_changed(name, action.currentText())
					if "editable" in data:
						action.setEditable(data["editable"])
					action.adjustSize()
					action.blockSignals(False)
				if collect:
					self.actions[name] = collect
		
		for action in self.actions[name]:
			if "caption" in data:
				action.setText(data["caption"])
			if ("icon" in data) and data["icon"]:
				action.setIcon(self.view.get_icon(data["icon"]))
			if "shortcut" in data:
				action.setShortcut(QtGui.QKeySequence(data["shortcut"]))
				if child_window:
					action.setShortcutContext(QtCore.Qt.ShortcutContext.WindowShortcut)
				else:
					action.setShortcutContext(QtCore.Qt.ShortcutContext.WidgetWithChildrenShortcut)
			if "help" in data:
				action.setToolTip(data["help"])
			if "checkable" in data:
				action.setCheckable(data["checkable"])
			if "checked" in data:
				action.setChecked(data["checked"])
			if "enabled" in data:
				action.setEnabled(data["enabled"])
	
	def set_toolbar_visible(self, name, state):
		
		if name not in self.toolbars:
			return
		self.toolbars[name].setVisible(state)
	
	def get_state(self, name):
		
		if name not in self.actions:
			return False
		return self.actions[name][0].isChecked()
	
	def get_combo_value(self, name):
		
		if (name in self.actions) and isinstance(self.actions[name][0], ComboAction):
			return self.actions[name][0].currentText()
	
	def set_combo_value(self, name, text):
		
		if (name in self.actions) and isinstance(self.actions[name][0], ComboAction):
			for action in self.actions[name]:
				action.blockSignals(True)
				action.setCurrentText(text)
				action.blockSignals(False)
	
	@QtCore.Slot(QtGui.QAction)
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
		
		self.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
		self.setEditable(True)

