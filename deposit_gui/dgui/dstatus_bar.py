'''
Generic class to be re-used also by Deposit in the future
'''

from PySide2 import (QtWidgets)

class DStatusBar(QtWidgets.QStatusBar):
	
	def __init__(self, view):
		
		QtWidgets.QStatusBar.__init__(self, view)
		
	def message(self, text):
		
		self.showMessage(text)

