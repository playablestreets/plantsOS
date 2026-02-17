#!/bin/bash

# Source the configuration file to access variables (if needed)
source "$(dirname "$0")/bop.config"

# Get the absolute path to the git repository root
GITREPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

# Define the hardcoded path to the sample packs destination directory
SAMPLES_DIR_PATH="$GITREPO_ROOT/pd/bop/samplepacks"

echo "Clearing all contents from: $SAMPLES_DIR_PATH"

# Remove all contents of the directory, but not the directory itself
rm -rf "$SAMPLES_DIR_PATH"/*

# Re-create the directory if it was deleted (in case it was empty to start with)
mkdir -p "$SAMPLES_DIR_PATH"

echo "Samplepacks cleared successfully!"