from deposit_gui.controller.controller import Controller
from deposit.utils.fnc_files import (clear_temp_dir)

from PySide2 import (QtWidgets)
import sys

class DGUIMain(object):
	
	def __init__(self, store: object = None) -> None:
		
		app = QtWidgets.QApplication(sys.argv)
		app.setStyle("Fusion")
		
		self.controller = Controller(store)
		self.controller.cview.show()
		self.controller.cdialogs.open("Connect")
		
		app.exec_()
	
	def __del__(self):
		
		clear_temp_dir()
