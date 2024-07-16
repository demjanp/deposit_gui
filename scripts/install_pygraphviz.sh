#!/bin/bash

# Define variables
REPO_URL="https://github.com/pygraphviz/pygraphviz.git"
TEMP_DIR=$(mktemp -d)

GRAPHVIZ_PREFIX=$(brew --prefix graphviz)
GRAPHVIZ_REAL_PATH=$(realpath $GRAPHVIZ_PREFIX)

# Clone the pygraphviz repository
git clone $REPO_URL $TEMP_DIR

cd $TEMP_DIR

# Modify setup.py to include the necessary paths
sed -i '' "s|include_dirs=\[\]|include_dirs=['${GRAPHVIZ_REAL_PATH}/include']|" setup.py
sed -i '' "s|library_dirs=\[\]|library_dirs=['${GRAPHVIZ_REAL_PATH}/lib']|" setup.py

# Build and install pygraphviz
python3 setup.py build
python3 setup.py install

# Clean up
cd ..
rm -rf $TEMP_DIR

echo "pygraphviz installation completed."
