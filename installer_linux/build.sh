#!/bin/bash

cd ..

rm -rf build
rm -rf dist

source .venv/bin/activate

python bin/update_imports.py installer_linux

pyinstaller installer_linux/dep_gui.spec

python installer_linux/make_appimage.py
