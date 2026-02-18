#!/bin/bash

BRANCH_NAME="$1"

cd /home/pi/plantsOS
echo "--- checking out $BRANCH_NAME"

# Attempt to checkout the branch
if git checkout "$BRANCH_NAME"; then
  echo "Successfully checked out branch: $BRANCH_NAME"
else
  echo "Error: Failed to checkout branch: $BRANCH_NAME"
  echo "Please ensure the branch exists or is a valid ref."
  exit 1
fi
