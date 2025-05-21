#!/bin/bash

set -e

chmod +x *.sh *.py

echo "[*] Running install.sh..."
sudo ./install.py

echo "[*] Running setup_suricata.sh..."
sudo ./setup_suricata.sh

echo "[*] Running setup_network_scan.sh..."
sudo ./setup_network_scan.sh

echo "[*] Running setup_active_pinging.sh..."
sudo ./setup_active_pinging.sh

echo "[*] Running remove_installation_files.sh..."
sudo ./remove_installation_files.sh