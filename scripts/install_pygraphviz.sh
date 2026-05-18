#!/bin/bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
	echo "Homebrew is required to install pygraphviz on macOS." >&2
	exit 1
fi

if ! brew list graphviz >/dev/null 2>&1; then
	brew install graphviz
fi

GRAPHVIZ_PREFIX="$(brew --prefix graphviz)"

python -m pip install --no-cache-dir \
	--config-settings=--global-option=build_ext \
	--config-settings=--global-option="-I${GRAPHVIZ_PREFIX}/include" \
	--config-settings=--global-option="-L${GRAPHVIZ_PREFIX}/lib" \
	'pygraphviz>=1.13,<2'

python -c "import pygraphviz"

echo "pygraphviz installation completed."
