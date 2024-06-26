#!/bin/bash

cd ..

rm -rf build
rm -rf dist

source .venv/bin/activate

python installer_mac/make_pkgproj.py

brew install graphviz

pyinstaller installer_mac/dep_gui.spec

if [ ! -d "Frameworks" ]; then
    bash installer_mac/collect_frameworks.sh
fi

cp -R 'Frameworks' 'dist'

python installer_mac/create_app.py