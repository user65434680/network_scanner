#!/bin/bash

sudo chmod +x *.sh *.py

sudo bash install.sh

sleep 15

sudo bash setup_suricata.sh

sleep 15

sudo python3 edit_yaml.py

sleep 15

sudo bash setup_network_scan.sh

sleep 15

sudo systemctl reboot