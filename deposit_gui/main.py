from deposit_gui.controller.controller import Controller
from deposit.utils.fnc_files import (clear_temp_dir)

from PySide2 import (QtWidgets)
import sys

class DGUIMain(object):
	
	def __init__(self, store: object = None) -> None:
		
		app = QtWidgets.QApplication(sys.argv)
		
		self.controller = Controller(store)
		
		app.exec_()
	
	def __del__(self):
		
		clear_temp_dir()
