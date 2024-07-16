from deposit_gui import DGUIMain
from deposit_gui.controller.controller import Controller

from PySide6 import QtWidgets, QtCore
import sys
import os

class DGUIMain_mod(DGUIMain, QtCore.QObject):
	
	def __init__(self):
		QtCore.QObject.__init__(self)
		
		self.app = QtWidgets.QApplication(sys.argv)
		
		self.timer = QtCore.QTimer()
		self.timer.setSingleShot(True)
		self.timer.timeout.connect(self.on_timer)
		
		self.controller = Controller(None)
		self.controller.cview.show()
		self.controller.cdialogs.open("Connect")
		self.timer.start(5000)

	def run(self):
		self.app.exec()
		
	@QtCore.Slot()
	def on_timer(self):
		self.controller.close()
		self.app.quit()

if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) != 1:
		raise Exception("Invalid number of arguments.\nCorrect use: update_imports.py <installer dir>")
	
	installer_dir, = args

	gui = DGUIMain_mod()

	# Use a single-shot QTimer to delay the execution of the remaining code
	def process_remaining():
		results = [m.__name__ for m in sys.modules.values() if m]
		results = sorted(results)
		txt = ",\n".join(["'%s'" % (name) for name in results])
		txt = f"imports=[\n{txt},\n]"
		fimports = os.path.join(installer_dir, 'hiddenimports.py')
		with open(fimports, "w") as f:
			f.write(txt)

	QtCore.QTimer.singleShot(0, process_remaining)
	gui.run()
