#!/bin/bash

# Source the configuration file to access variables
source "$(dirname "$0")/bopos.config"

# Get the absolute path to the git repository root
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the new, hardcoded path for the sample packs destination directory
SAMPLES_DIR_PATH="$GITREPO_ROOT/pd/bop/samplepacks"

# Define a temporary file for the downloaded zip
TEMP_ZIP_FILE=$(mktemp)

echo "Downloading sample packs from $SAMPLEPACKSURL..."
# Download the zip file
curl -L -o "$TEMP_ZIP_FILE" "$SAMPLEPACKSURL"

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# Get the name of the top-level directory inside the zip file
# unzip -l lists the contents, head -n 5 gets the top lines, awk gets the 4th field (filename), and grep cleans up.
# This assumes the zip file has a single root directory.
ZIP_ROOT_FOLDER=$(unzip -l "$TEMP_ZIP_FILE" | head -n 5 | awk '{print $4}' | grep '/' | head -n 1 | cut -d'/' -f1)

# Check if a root folder was found
if [ -z "$ZIP_ROOT_FOLDER" ]; then
    echo "Error: Could not determine the top-level folder in the zip file."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# Construct the path to the specific folder to be overwritten
FOLDER_TO_OVERWRITE="$SAMPLES_DIR_PATH/$ZIP_ROOT_FOLDER"

# Check if the folder to be overwritten already exists and delete it
if [ -d "$FOLDER_TO_OVERWRITE" ]; then
    echo "Cleaning up existing folder: $FOLDER_TO_OVERWRITE"
    rm -rf "$FOLDER_TO_OVERWRITE"
fi

echo "Creating destination directory if it doesn't exist: $SAMPLES_DIR_PATH"
# Create the directory if it doesn't already exist
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

# Clean up the temporary zip file
rm "$TEMP_ZIP_FILE"

echo "Sample packs updated successfully!"
exit 0
