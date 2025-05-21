#!/bin/bash
SCRIPT_PATH="/opt/active_pinging/active_pinging.py"
SERVICE_PATH="/etc/systemd/system/active_pinging.service"

if [[ "$EUID" -ne 0 ]]; then
  echo "Please run this script as root or with sudo."
  exit 1
fi
mkdir -p /opt/active_pinging
sudo cp active_pinging.py "$SCRIPT_PATH"

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
RequiresMountsFor=/opt/active_pinging /etc/systemd/system

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/active_pinging/active_pinging.py"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

echo "Created systemd service file at $SERVICE_PATH."


systemctl daemon-reexec
systemctl daemon-reload
systemctl enable active_pinging.service"

echo "Service enabled to run on boot: active_pinging.service""

echo "Setting permissions..."
sudo chmod 700 /opt/active_pinging
sudo chmod 700 /opt/active_pinging/active_pinging.py"
sudo chown root:root /opt/active_pinging/active_pinging.py"

echo "Starting network scan service..."
sudo systemctl start active_pinging.service"
