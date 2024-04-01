#!/bin/bash
set -xe

# Check if the script is being run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

echo 'Copying files to /opt/stonkes-worker...'
# Install the stock it files
rsync -a ./v1/ /opt/stonkes-worker
chmod +x /opt/stonkes-worker/install_dependencies.sh
echo "Installed stock it files to /opt/stonkes-worker"
echo "Installing dependencies..."
(cd /opt/stonkes-worker && ./install_dependencies.sh)
echo "Dependencies installed successfully"

echo "Installing stonkes-worker.service..."

cp ./v1/start.sh /usr/local/bin/stonkes-worker.sh
chmod +x /usr/local/bin/stonkes-worker.sh

#echo "#!/bin/bash" > /usr/local/bin/stonkes-worker.sh
#echo "python -u \"/opt/stonkes-worker/main.py\"" >> /usr/local/bin/stonkes-worker.sh

# Copy the .service file to the systemd directory
cp ./stonkes-worker.service /etc/systemd/system/
cp ./stonkes-worker.timer /etc/systemd/system/

# Reload systemd to detect the new service
systemctl daemon-reload

# Enable the service to start on boot
systemctl enable stonkes-worker.service
systemctl enable stonkes-worker.timer

# Start the service
systemctl start stonkes-worker.service
systemctl start stonkes-worker.timer

echo "Service stonkes-worker.service installed and started successfully"
