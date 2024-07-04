#!/bin/bash

temp_file="$1"
joined_list="$2"

IFS=',' read -r -a libraries <<< "$joined_list"

cleanup() {
  echo "1" > "$temp_file"
  exit 1
}
trap cleanup SIGINT SIGTERM

echo "0" > "$temp_file"

# Function to check if a command exists
command_exists() {
	command -v "$1" &>/dev/null
}

# Check if xcode-select is installed
if ! command_exists xcode-select; then
	echo "xcode-select not found. Installing Xcode Command Line Tools..."
	xcode-select --install
	
	if ! command_exists xcode-select; then
		echo "1" > "$temp_file"
		exit 1
	fi
else
	echo "xcode-select is already installed."
fi

# Check if Homebrew is installed
if ! command_exists brew; then
	echo "Homebrew not found. Installing Homebrew..."
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	
	if ! command_exists brew; then
		echo "1" > "$temp_file"
		exit 1
	fi
else
	echo "Homebrew is already installed."
fi

# Ensure Homebrew is up to date
echo "Updating Homebrew..."
brew update

# Check and install graphviz, poppler, and tesseract

for library in "${libraries[@]}"; do
	if ! brew list --formula | grep -q "^${library}\$"; then
		echo "${library} not found. Installing ${library}..."
		brew install "${library}"
	else
		echo "${library} is already installed."
	fi
done

echo "Script execution completed."
echo "2" > "$temp_file"

