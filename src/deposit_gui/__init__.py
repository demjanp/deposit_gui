version_info = (1, 4, 2)

__version__ = '.'.join(map(str, version_info))
__title__ = 'Deposit'
__date__ = "9.9.2022"

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
from deposit_gui.dgui.dview import DView
