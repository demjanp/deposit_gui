#!/bin/bash

cd ..

rm -rf build/dep_gui
rm -rf dist/deposit_gui

source .venv/bin/activate

python -m build

pyinstaller installer_mac/dep_gui.spec
