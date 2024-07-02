# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

path = 'installer_mac/hiddenimports.py'
with open(path, 'r') as file:
    file_content = file.read()
imports = []
exec(file_content)

a = Analysis(
    ['../bin/start_gui.py'],
    pathex=['.venv/lib/python3.10/site-packages'],
    binaries=[],
    datas=[
        ('../src/deposit_gui/res', 'deposit_gui/res'),
        ('../src/deposit_gui/dgui/qss', 'deposit_gui/dgui/qss'),
        ('../src/deposit_gui/utils', 'deposit_gui/utils'),
        ('../LICENSE', '.'),
        ('../THIRDPARTY.TXT', '.'),
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

