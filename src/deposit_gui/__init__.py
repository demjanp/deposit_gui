from ._meta import title as __title__, date as __date__, __version__

import os
import sys

if sys.platform == "darwin":
	import shutil
	from .utils.download_libs import download_mac_libs
	
	os.environ["PATH"] += os.pathsep + "/usr/local/bin"
	
	found_graphviz = (shutil.which("dot") is not None)
	if not found_graphviz:
		found_graphviz = download_mac_libs(["graphviz"])
	if not found_graphviz:
		raise Exception("Graphviz not found")

elif sys.platform == "win32":
	from deposit_gui.utils.download_libs import download_win_libs
	
	download_win_libs()

from deposit_gui.dgui_main import DGUIMain

from deposit_gui.dgui.abstract_subcontroller import AbstractSubcontroller
from deposit_gui.dgui.abstract_subview import AbstractSubview
from deposit_gui.dgui.dclickable_logo import DClickableLogo
from deposit_gui.dgui.dconnect_frame import DConnectFrame
from deposit_gui.dgui.dgraphics_view import DGraphicsView
from deposit_gui.dgui.dnotification import DNotification
from deposit_gui.dgui.dmain_window import DMainWindow
from deposit_gui.dgui.dgraph_view import DGraphView
from deposit_gui.dgui.dregistry import DRegistry
from deposit_gui.dgui.dcactions import DCActions
from deposit_gui.dgui.dcdialogs import DCDialogs
from deposit_gui.dgui.dcmodel import DCModel
from deposit_gui.dgui.dview import DView
