from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.dgui.dvactions import DVActions

from PySide6 import (QtCore)

class DCActions(AbstractSubcontroller):
	
	def __init__(self, cmain, cview) -> None:
		
		AbstractSubcontroller.__init__(self, cmain)
		
		self._vactions = DVActions(cview._view)
		
		self._vactions.toolbar.signal_triggered.connect(self.on_toolbar_triggered)
		self._vactions.toolbar.signal_combo_changed.connect(self.on_toolbar_combo_changed)
		self._vactions.menubar.signal_triggered.connect(self.on_menubar_triggered)
		
		self._vactions.toolbar.populate(self.set_up_tool_bar())
		self._vactions.menubar.populate(self.set_up_menu_bar())
	
	def update(self):
		
		for bar in [self._vactions.toolbar, self._vactions.menubar]:
			for name in bar.get_names():
				if hasattr(self, "update_%s" % (name)):
					bar.update_tool(name, getattr(self, "update_%s" % (name))())
	
	@QtCore.Slot(str)
	def on_toolbar_triggered(self, name):
		
		if hasattr(self, "on_%s" % (name)):
			getattr(self, "on_%s" % (name))(self._vactions.toolbar.get_state(name))
	
	@QtCore.Slot(str, str)
	def on_toolbar_combo_changed(self, name, text):
		
		if hasattr(self, "on_%s" % (name)):
			getattr(self, "on_%s" % (name))(text)
	
	@QtCore.Slot(str)
	def on_menubar_triggered(self, name):
		
		if hasattr(self, "on_%s" % (name)):
			getattr(self, "on_%s" % (name))(self._vactions.menubar.get_state(name))
	
	# ---- Signal handling
	# ------------------------------------------------------------------------
	
	
	# ---- get/set
	# ------------------------------------------------------------------------
	def get_combo_value(self, name):
		
		return self._vactions.toolbar.get_combo_value(name)
		
	def set_combo_value(self, name, text):
		
		self._vactions.toolbar.set_combo_value(name, text)
	
	
	# ---- Actions
	# ------------------------------------------------------------------------
	def set_up_tool_bar(self):
		# re-implement to fill tool bar
		
		return {}
		'''
		return {
			"Toolbar": [
				("Name", "Caption"),
				("Name", "Caption"),
			],
		}
		'''
	
	def set_up_menu_bar(self):
		# re-implement to fill menu bar
		
		return {}
		'''
		return {
			"Menu": [
				("Name", "Caption"),
				("Name", "Caption"),
			],
		}
		'''
	
	
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
	
	def on_[name](self, state / text):
		
		pass
	'''
