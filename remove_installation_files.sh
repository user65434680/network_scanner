#!/bin/bash

# Remove installation files
sudo rm run_all.sh
sudo rm install.py
sudo rm setup_suricata.sh
sudo rm setup_network_scan.sh
sudo rm network_scan.py
sudo rm setup_active_pinging.sh
sudo rm active_pinging.py

echo "[*] Scheduling system reboot in 10 seconds..."
sudo shutdown -r +1 "System will reboot in 10 seconds"

rm -- "$0"
