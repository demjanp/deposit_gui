#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

rm -rf build
rm -rf dist

if ! command -v brew >/dev/null 2>&1; then
	echo "Homebrew is required to build the macOS installer." >&2
	exit 1
fi

if ! brew list graphviz >/dev/null 2>&1; then
	brew install graphviz
fi

source .venv/bin/activate

if ! python -c "import pygraphviz" >/dev/null 2>&1; then
	bash scripts/install_pygraphviz.sh
fi

python installer_mac/make_pkgproj.py

python bin/update_imports.py installer_mac

pyinstaller --clean installer_mac/dep_gui.spec

find dist/dep_gui -type d -name "__pycache__" -exec rm -r {} +

python installer_mac/create_app.py
