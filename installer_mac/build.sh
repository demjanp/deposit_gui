#!/bin/bash

cd ..

rm -rf build
rm -rf dist

source .venv/bin/activate

python installer_mac/make_pkgproj.py

brew install graphviz

pyinstaller installer_mac/dep_gui.spec

find dist/dep_gui -type d -name "__pycache__" -exec rm -r {} +

python installer_mac/create_app.py