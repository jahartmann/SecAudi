#!/usr/bin/env bash
set -euo pipefail

# Update and upgrade system packages
sudo apt-get update
sudo apt-get upgrade -y

# Ensure pip is available
sudo apt-get install -y python3-pip

# Install Python dependencies
pip3 install --upgrade pip
pip3 install -r requirements.txt
