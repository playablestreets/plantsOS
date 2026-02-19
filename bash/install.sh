#!/bin/bash
# plantsOS unattended installation script
# This script automates the install packages section from the README for a headless Raspberry Pi setup.
# Run as: bash install_plantsos.sh

set -e

# Update and upgrade Raspbian
sudo apt-get update && sudo apt-get upgrade -y

# Enable i2c and expand filesystem (requires user interaction, so we skip this for unattended)
# sudo raspi-config nonint do_i2c 0
# sudo raspi-config --expand-rootfs
# Note: For full automation, consider pre-configuring raspi-config via CLI or image customization.

# Install required packages
sudo apt-get install -y jackd2 git python3-pip puredata python3-venv

# Accept jack realtime priority automatically (if needed)
# This may require additional configuration for full automation.

# Create Python virtual environment
cd ~
python3 -m venv ./venv

# Clone plantsOS repository if not already present
if [ ! -d "plantsOS" ]; then
    git clone https://github.com/playablestreets/plantsOS.git
fi

# Install Python dependencies
~/venv/bin/pip install -r ~/plantsOS/python/requirements.txt

# Run update script
echo "Running update script..."
sudo ~/plantsOS/bash/update.sh
