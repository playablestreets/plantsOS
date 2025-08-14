#!/bin/bash

# Source the configuration file to access variables
# This is still necessary for SAMPLESPACKSURL
source "$(dirname "$0")/bop.config"

# Get the absolute path to the git repository root
# This corresponds to ~/plantsOS
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the new, hardcoded path for the sample packs directory
# This overrides the SAMPLEPACKSDIR variable from the config
SAMPLES_DIR_PATH="$GITREPO_ROOT/pd/bop/samplepacks"

# Define a temporary file for the downloaded zip
TEMP_ZIP_FILE=$(mktemp)

echo "Downloading sample packs from $SAMPLESPACKSURL..."
# Download the zip file
curl -L -o "$TEMP_ZIP_FILE" "$SAMPLESPACKSURL"

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

echo "Creating destination directory if it doesn't exist: $SAMPLES_DIR_PATH"
# Create the directory if it doesn't already exist
mkdir -p "$SAMPLES_DIR_PATH"

echo "Extracting and overwriting sample packs in $SAMPLES_DIR_PATH..."
# Unzip the downloaded file directly into the new directory, overwriting existing files
unzip -o "$TEMP_ZIP_FILE" -d "$SAMPLES_DIR_PATH"

# Check if the unzip was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to extract sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# Clean up the temporary zip file
rm "$TEMP_ZIP_FILE"

echo "Sample packs updated successfully!"
exit 0
