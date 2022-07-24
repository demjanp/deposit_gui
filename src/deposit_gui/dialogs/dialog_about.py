#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from deposit_gui import __version__, __date__
import deposit_gui

from PySide2 import (QtWidgets, QtCore, QtGui)
import os

class DialogAbout(QtWidgets.QFrame):
	
	def __init__(self):
		
		QtWidgets.QFrame.__init__(self)
		
		self.setMinimumWidth(400)
		self.setLayout(QtWidgets.QVBoxLayout())
		
		content = QtWidgets.QFrame()
		content.setLayout(QtWidgets.QHBoxLayout())
		self.layout().addWidget(content)
		
		logo = QtWidgets.QLabel()
		logo.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(deposit_gui.__file__), "res/deposit_logo.svg")))
		path = os.path.join(os.path.dirname(deposit_gui.__file__), "THIRDPARTY.TXT").replace("\\", "/")
		label = QtWidgets.QLabel('''
<h2>Deposit</h2>
<h4>Graph-based data storage and exchange</h4>
<p>Version %s (%s)</p>
<p>Copyright © <a href="mailto:peter.demjan@gmail.com">Peter Demján</a> 2013 - %s</p>
<p>&nbsp;</p>
<p>Licensed under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License</a></p>
<p><a href="https://github.com/demjanp/deposit">Home page</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="%s">Third party libraries</a></p>
		''' % (__version__, __date__, __date__.split(".")[-1], path))
		label.setOpenExternalLinks(True)
		content.layout().addWidget(logo)
		content.layout().addWidget(label)
