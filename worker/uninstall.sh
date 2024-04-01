#!/bin/bash

# Check if the script is being run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# Stop the service
systemctl stop stonkes-worker.service

# Remove the service
systemctl disable stonkes-worker.service

# Remove the service file
rm /etc/systemd/system/stonkes-worker.service

# Remove the worker files
rm -rf /opt/stonkes-worker
# Remove the shell files
rm /usr/local/bin/stonkes-worker.sh

echo "Uninstalled stonkes-worker"