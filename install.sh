#!/bin/bash

set -e

echo "[*] Updating package lists..."
sudo apt update

echo "[*] Installing Suricata and related tools..."
sudo apt install -y suricata jq python3-pip

if ! command -v suricata-update &> /dev/null; then
    echo "[*] Installing suricata-update via pip..."
    sudo pip3 install --upgrade suricata-update
fi

echo "[*] Updating Suricata rules..."
sudo suricata-update

echo "[*] Enabling Suricata to start on boot..."
sudo systemctl enable suricata

echo "[*] Starting Suricata service..."
sudo systemctl start suricata

echo "[*] Suricata status:"
sudo systemctl status suricata --no-pager

echo "[*] Suricata logs will be written to /var/log/suricata/"
echo "[*] Fast log: /var/log/suricata/fast.log"
echo "[*] JSON log: /var/log/suricata/eve.json"

echo "[*] To monitor alerts in real time, run:"
echo "    sudo tail -f /var/log/suricata/fast.log"
