#!/bin/bash

# Source the configuration file to access variables
source "$(dirname "$0")/bopos.config"

# Get the absolute path to the git repository root
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the hardcoded path for the sample packs destination directory
SAMPLES_DIR_PATH="$GITREPO_ROOT/pd/bop/samplepacks"

# Define a temporary file for the downloaded zip
TEMP_ZIP_FILE=$(mktemp)

# Define the folder name manually to avoid the "uc" issue
FOLDER_NAME="sample_archive"

echo "Downloading sample packs from $SAMPLEPACKSURL..."
# Download the zip file using gdown
/home/pi/venv/bin/gdown --fuzzy "$SAMPLEPACKSURL" -O "$TEMP_ZIP_FILE"

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to download sample packs."
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

# --- SIMPLIFIED CODE: Forcefully move contents up one level ---
echo "Correcting folder structure: Moving contents of inner folder up one level."

# Move all contents from that inner folder to the parent folder
cp -r "$TARGET_FOLDER_PATH/*" "../$TARGET_FOLDER_PATH"


# Clean up the temporary zip file
rm "$TEMP_ZIP_FILE"
rm -r "$TARGET_FOLDER_PATH"

echo "Sample packs updated successfully!"
exit 0
