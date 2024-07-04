# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

block_cipher = None

sys.path.insert(0, os.path.abspath('installer_linux/custom_hooks'))

hiddenimports = collect_submodules('deposit_gui') + collect_submodules('networkit')
binaries = collect_dynamic_libs('deposit_gui') + collect_dynamic_libs('networkit')

path = 'installer_linux/hiddenimports.py'
with open(path, 'r') as file:
    file_content = file.read()
imports = []
exec(file_content)

imports += [
    'deposit_gui',
    '_struct',
    'struct',
    'pyi_rth_multiprocessing',
    'pyi_rth_pkgres',
    'pkg_resources',
    'pkg_resources.py2_warn',
    'pkg_resources.markers',
    'pkg_resources._vendor',
    'pkg_resources._vendor.packaging',
    'pkg_resources.extern',
]
hiddenimports.extend(imports)

datas=[
    ('../src/deposit_gui/res', 'deposit_gui/res'),
    ('../src/deposit_gui/dgui/qss', 'deposit_gui/dgui/qss'),
    ('../src/deposit_gui/utils', 'deposit_gui/utils'),
    ('../LICENSE', '.'),
    ('../THIRDPARTY.TXT', '.'),
]

a = Analysis(
    ['../bin/start_gui.py'],
    pathex=['.venv/lib/python3.10/site-packages'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['installer_linux/custom_hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['sip', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dep_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Important for macOS to handle double-click events properly
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../src/deposit_gui/res/deposit_icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dep_gui',
    distpath='dist/deposit_gui',
    excludes=[],
)

