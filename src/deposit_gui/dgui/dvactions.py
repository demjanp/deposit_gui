'''
VActions(AbstractSubview)
	.toolbar
		.signal_triggered = Signal(name)
		.signal_combo_changed = Signal(name, text)
		.populate(tools)
		.get_names()
		.update_tool(name, data, child_window = False, clear_combo_text = False)
		.set_toolbar_visible(name, state)
		.get_state(name)
		.get_combo_value(name)
		.set_combo_value(name, text)
	.menubar
		same as toolbar

'''

from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.dgui.dtool_bar import DToolBar
from deposit_gui.dgui.dmenu_bar import DMenuBar

from PySide6 import (QtCore)

class DVActions(AbstractSubview):
	
	def __init__(self, vmain) -> None:
		
		AbstractSubview.__init__(self, vmain)
		
		# implement each action behaviour via lap.controller.cactions
		
		self.toolbar = DToolBar(self.vmain)
		self.menubar = DMenuBar(self.vmain)
