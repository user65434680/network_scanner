#!/bin/bash

# setup network scanner for controller
SCRIPT_PATH="/opt/network_scan/network_scan.py"
SERVICE_PATH="/etc/systemd/system/network_scan.service"

if [[ "$EUID" -ne 0 ]]; then
  echo "Please run this script as root or with sudo."
  exit 1
fi
mkdir -p /opt/network_scan
sudo cp network_scan.py "$SCRIPT_PATH"

if [[ -f "$SCRIPT_PATH" ]]; then
  chmod +x "$SCRIPT_PATH"
  echo "Made $SCRIPT_PATH executable."
else
  echo "Error: Script $SCRIPT_PATH does not exist."
  exit 1
fi

cat <<EOF > "$SERVICE_PATH"
[Unit]
Description=Network Scan Service
After=network-online.target 
Wants=network-online.target
RequiresMountsFor=/opt/network_scan /etc/systemd/system

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/network_scan/network_scan.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

echo "Created systemd service file at $SERVICE_PATH."


systemctl daemon-reexec
systemctl daemon-reload
systemctl enable network_scan.service

echo "Service enabled to run on boot: network_scan.service"

echo "Setting permissions..."
sudo chmod 700 /opt/network_scan
sudo chmod 700 /opt/network_scan/network_scan.py
sudo chown root:root /opt/network_scan/network_scan.py
