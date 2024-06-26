# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.building.datastruct import TOC

from deposit_gui.utils.download_libs import download_libs
download_libs()

block_cipher = None

path = 'installer_win\\hiddenimports.py'
with open(path, 'r') as file:
    file_content = file.read()
imports = []
exec(file_content)

a = Analysis(
	['..\\bin\\start_gui.py'],
	pathex=['.venv\\Lib\\site-packages'],
	binaries=[],
	datas=[
			('..\\src\\deposit_gui\\dgui\\graphviz_win', 'deposit_gui\\dgui\\graphviz_win'),
			('..\\src\\deposit_gui\\dgui\\pygraphviz', 'deposit_gui\\dgui\\pygraphviz'),
			('..\\src\\deposit_gui\\res', 'deposit_gui\\res'),
			('..\\LICENSE', '.'),
			('..\\THIRDPARTY.TXT', '.'),
		],
	hiddenimports=[
		'deposit_gui',
		'networkit.base',
		'networkit.helpers',
		'networkit.traversal',
		'scipy.io',
	] + imports,
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=['sip', 'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False,
)

x = 'cp36-win_amd64'
datas_upd = TOC()

for d in a.datas:
	if x not in d[0] and x not in d[1]:
		datas_upd.append(d)

a.datas = datas_upd

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
	pyz,
	a.scripts,
	[],
	exclude_binaries=True,
	name='deposit_gui',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	icon='..\\src\\deposit_gui\\res\\deposit_icon.ico',
)
coll = COLLECT(
	exe,
	a.binaries,
	a.zipfiles,
	a.datas,
	strip=False,
	upx=True,
	upx_exclude=[],
	name='deposit_gui',
	distpath='dist/deposit_gui',
)
