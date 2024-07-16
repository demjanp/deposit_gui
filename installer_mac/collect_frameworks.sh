#!/bin/bash

to_abs_path() {
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

copy_app() {
    local app_name=$1
    local app_path=$2
    dest_dir=$INSTALLER_DIR/$app_name
    mkdir -p "$dest_dir"
    cp -R "$app_path"/* "$dest_dir"
}

display_progress() {
    local title=$1
    local current=$2
    local total=$3
    local progress=$((current * 100 / total))
    local done=$((progress / 2))
    local left=$((50 - done))
    printf "\r%s: [" "$title"
    printf "%0.s#" $(seq 1 $done)
    printf "%0.s " $(seq 1 $left)
    printf "] %d%% (%d/%d)" $progress $current $total
}

INSTALLER_DIR=Frameworks

if [ "$#" -eq 1 ]; then
# Convert provided arguments to absolute paths
    INSTALLER_DIR=$(to_abs_path "$1/Frameworks")
fi

rm -rf "$INSTALLER_DIR"
mkdir "$INSTALLER_DIR"

# Uninstall and reinstall specified packages
brew uninstall poppler tesseract
brew uninstall graphviz

# Get the list of currently installed formulae
EXCLUDED_APPS=$(brew list --formula)

# Install the specified packages
brew install graphviz

# Get the list of all installed formulae after installation
INSTALLED_APPS=$(brew list --formula)
FOUND_APPS=()
counter=0
total_apps=$(echo "$INSTALLED_APPS" | wc -w)

# Function to check if an app is in the excluded list
is_excluded() {
    local app=$1
    for excluded_app in $EXCLUDED_APPS; do
        if [[ "$excluded_app" == "$app" ]]; then
            return 0
        fi
    done
    return 1
}

# Inspect installed apps and exclude the pre-existing ones
for app in $INSTALLED_APPS; do
    counter=$((counter + 1))
    display_progress "Inspecting" $counter $total_apps
    if ! is_excluded "$app"; then
        FOUND_APPS+=("$app")
    fi
done

counter=0
total_apps=${#FOUND_APPS[@]}

# Add new apps to the installer directory
for app in "${FOUND_APPS[@]}"; do
    counter=$((counter + 1))
    display_progress "Adding" $counter $total_apps
    APP_PREFIX=$(brew --prefix "$app")
    APP_VERSION=$(brew info --json=v1 "$app" | jq -r '.[0].versions.stable')
    if [ -n "$APP_PREFIX" ] && [ -n "$APP_VERSION" ]; then
        REAL_PATH=$(realpath "$APP_PREFIX")
        copy_app "$app" "$REAL_PATH"
    fi
done
