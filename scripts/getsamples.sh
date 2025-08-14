#!/bin/bash

# Source the configuration file to access variables
source "$(dirname "$0")/bopos.config"

# Get the absolute path to the git repository root
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the hardcoded path for the sample packs destination directory
SAMPLES_DIR_PATH="$GITREPO_ROOT/pd/bop/samplepacks"

# Define a temporary file for the downloaded zip
TEMP_ZIP_FILE=$(mktemp)

echo "Downloading sample packs from $SAMPLEPACKSURL..."
# Download the zip file
#curl -L -o "$TEMP_ZIP_FILE" "$SAMPLEPACKSURL"

/home/pi/venv/bin/gdown "$SAMPLEPACKSURL" -O "$TEMP_ZIP_FILE" 

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download sample packs."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# Get the name of the downloaded zip file from the URL
# The 'basename' command gets the filename, and a parameter expansion strips the .zip extension
ZIP_FILENAME=$(basename "$SAMPLEPACKSURL" | cut -d'?' -f1)
FOLDER_NAME="${ZIP_FILENAME%.zip}"

# Check if a valid folder name was extracted
if [ -z "$FOLDER_NAME" ]; then
    echo "Error: Could not determine the folder name from the URL."
    rm "$TEMP_ZIP_FILE"
    exit 1
fi

# Define the full path to the folder that will contain the extracted files
TARGET_FOLDER_PATH="$SAMPLES_DIR_PATH/$FOLDER_NAME"

echo "Clearing and recreating target folder: $TARGET_FOLDER_PATH"
# Remove the existing folder and its contents to ensure a clean slate
rm -rf "$TARGET_FOLDER_PATH"

# Create the new, empty folder
mkdir -p "$TARGET_FOLDER_PATH"

echo "Extracting sample packs to $TARGET_FOLDER_PATH..."
# Unzip the downloaded file directly into the newly created folder
unzip -o "$TEMP_ZIP_FILE" -d "$TARGET_FOLDER_PATH"

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
