#!/bin/bash

chmod +x ../start.sh

# Check if the script is being run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi
# Copy the .service file to the systemd directory
cp ./stonkes-worker.service /etc/systemd/system/

# Reload systemd to detect the new service
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable stonkes-worker.service

# Start the service
systemctl start stonkes-worker.service

echo "Service stonkes-worker.service installed and started successfully"
