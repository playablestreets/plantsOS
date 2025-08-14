#!/bin/bash

# Source the configuration file to access variables
# This is still necessary for SAMPLEPACKSURL
source "$(dirname "$0")/bopos.config"

# Get the absolute path to the git repository root
# This corresponds to ~/plantsOS
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the new, hardcoded path for the sample packs directory
# This overrides the SAMPLEPACKSDIR variable from the config
SAMPLES_DIR_PATH="$GITREPO_ROOT/bop/samplepacks"

# Define a temporary file for the downloaded zip
TEMP_ZIP_FILE=$(mktemp)

# Get the current user
CURRENT_USER=$(whoami)

echo "Downloading sample packs from $SAMPLEPACKSURL..."
# Download the zip file
curl -L -o "$TEMP_ZIP_FILE" "$SAMPLEPACKSURL"

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

echo "Cleaning up existing sample packs directory: $SAMPLES_DIR_PATH"
# Remove the existing directory and its contents
rm -rf "$SAMPLES_DIR_PATH"

echo "Creating new directory: $SAMPLES_DIR_PATH"
# Create the new, empty directory
mkdir -p "$SAMPLES_DIR_PATH"

echo "Extracting sample packs to $SAMPLES_DIR_PATH..."
# Unzip the downloaded file directly into the new directory
unzip -o "$TEMP_ZIP_FILE" -d "$SAMPLES_DIR_PATH"

# Check if the unzip was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# echo "Setting ownership of $SAMPLES_DIR_PATH to $CURRENT_USER..."
# # Change the owner of the directory and its contents recursively
# chown -R "$CURRENT_USER":"$CURRENT_USER" "$SAMPLES_DIR_PATH"

# # Clean up the temporary zip file
# rm "$TEMP_ZIP_FILE"

echo "Sample packs updated and ownership set successfully!"
exit 0
