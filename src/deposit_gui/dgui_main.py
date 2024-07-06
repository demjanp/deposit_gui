from deposit_gui.controller.controller import Controller
from deposit.utils.fnc_files import (clear_temp_dir)

from PySide6 import (QtWidgets)
import sys
import os

class DGUIMain(object):
	
	def __init__(self, store: object = None) -> None:
		
		app = QtWidgets.QApplication.instance()
		if not app:
			app = QtWidgets.QApplication(sys.argv)
		
		self.controller = Controller(store)
		self.controller.cview.show()
		self.controller.cdialogs.open("Connect")
		
		app.exec()
	
	def __del__(self):
		
		clear_temp_dir()
