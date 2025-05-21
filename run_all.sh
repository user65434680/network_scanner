#!/bin/bash

set -e  # Exit on any error

chmod +x *.sh *.py

echo "[*] Running install.sh..."
sudo ./install.py

echo "[*] Running setup_suricata.sh..."
sudo ./setup_suricata.sh

echo "[*] Running edit_yaml.py..."
sudo ./edit_yaml.py

echo "[*] Running setup_network_scan.sh..."
sudo ./setup_network_scan.sh

echo "[*] Rebooting system in 10 seconds. Press Ctrl+C to cancel..."
sleep 10
sudo systemctl reboot