from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db import DConnectTabDB

from deposit.datasource import DBRel

from PySide2 import (QtWidgets, QtCore, QtGui)

class DConnectTabDBRel(DConnectTabDB):
	
	DATASOURCE = DBRel
