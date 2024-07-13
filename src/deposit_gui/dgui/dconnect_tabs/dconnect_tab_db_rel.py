from deposit_gui.dgui.dconnect_tabs.dconnect_tab_db import DConnectTabDB

from deposit.datasource import DBRel

class DConnectTabDBRel(DConnectTabDB):
	
	DATASOURCE = DBRel
