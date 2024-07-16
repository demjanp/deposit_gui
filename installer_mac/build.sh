#!/bin/bash

# Function to convert a relative path to an absolute path
to_abs_path() {
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# Default values for arguments as absolute paths
DEFAULT_ARG1="$(to_abs_path "../../deposit_frameworks")"

# If no arguments are provided, use default values
if [ "$#" -eq 0 ]; then
    ARG1=$DEFAULT_ARG1
elif [ "$#" -ne 1 ]; then
    echo "Usage: $0 [<frameworks dir>]"
    exit 1
else
    # Convert provided arguments to absolute paths
    ARG1=$(to_abs_path "$1")
fi

cd ..

rm -rf build
rm -rf dist

source .venv/bin/activate

python installer_mac/make_pkgproj.py

brew install graphviz

python bin/update_imports.py installer_mac

pyinstaller installer_mac/dep_gui.spec

find dist/dep_gui -type d -name "__pycache__" -exec rm -r {} +

if [ ! -d "$ARG1/Frameworks" ]; then
    bash installer_mac/collect_frameworks.sh "$ARG1"
fi

cp -R "$ARG1/Frameworks" "dist"

python installer_mac/create_app.py