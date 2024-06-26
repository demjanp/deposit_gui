from deposit_gui.controller.controller import Controller
from deposit.utils.fnc_files import (clear_temp_dir)

from PySide2 import (QtWidgets)
import sys
import os

if sys.platform == "darwin":
	frameworks_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Frameworks'))
	if os.path.isdir(frameworks_path):
		path_items = []
		dyld_items = []
		for framework in os.listdir(frameworks_path):
			path_items.append(os.path.join(frameworks_path, framework, 'bin'))
			dyld_items.append(os.path.join(frameworks_path, framework, 'lib'))
		os.environ['PATH'] = os.environ.get('PATH', '') + ":" + ':'.join(path_items)
		os.environ['DYLD_LIBRARY_PATH'] = os.environ.get('DYLD_LIBRARY_PATH', '') + ":" + ':'.join(dyld_items)

class DGUIMain(object):
	
	def __init__(self, store: object = None) -> None:
		
		app = QtWidgets.QApplication(sys.argv)
		
		self.controller = Controller(store)
		self.controller.cview.show()
		self.controller.cdialogs.open("Connect")
		
		app.exec_()
	
	def __del__(self):
		
		clear_temp_dir()
