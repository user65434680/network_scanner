#!/usr/bin/env python3

import os
import subprocess
import sys
from create_IP_file import extract_ips_from_inventory

def control_menu():
    while True:
        print("\nControl menu for starting and stopping Suricata, network_scan.service and active_pinging.service")
        print("1. Start Suricata")
        print("2. Stop Suricata")
        print("3. Start network_scan.service")
        print("4. Stop network_scan.service")
        print("5. Start active_pinging.service")
        print("6. Stop active_pinging.service")
        print("7. Change allowed IPs for active_pinging.service")
        print("8. Exit")

        control_choice = input("Select an option (1-8): ").strip()

        try:
            if control_choice == "1":
                print("Starting Suricata...")
                subprocess.run(["sudo", "systemctl", "start", "suricata.service"], check=True)
            elif control_choice == "2":
                print("Stopping Suricata...")
                subprocess.run(["sudo", "systemctl", "stop", "suricata.service"], check=True)
            elif control_choice == "3":
                print("Starting network_scan.service...")
                subprocess.run(["sudo", "systemctl", "start", "network_scan.service"], check=True)
            elif control_choice == "4":
                print("Stopping network_scan.service...")
                subprocess.run(["sudo", "systemctl", "stop", "network_scan.service"], check=True)
            elif control_choice == "5":
                print("Starting active_pinging.service...")
                subprocess.run(["sudo", "systemctl", "start", "active_pinging.service"], check=True)
            elif control_choice == "6":
                print("Stopping active_pinging.service...")
                subprocess.run(["sudo", "systemctl", "stop", "active_pinging.service"], check=True)
            elif control_choice == "7":
                extract_ips_from_inventory()
            elif control_choice == "8":
                print("Exiting control menu.")
                sys.exit(0)
            else:
                print("Invalid choice. Please select a valid option (1-8).")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")

if __name__ == "__main__":
    control_menu()