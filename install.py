#!/usr/bin/env python3

import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, shell=False):
    """Run a command and check its return code"""
    try:
        if isinstance(command, str) and shell:
            subprocess.run(command, shell=True, check=True)
        else:
            subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def main():
    print("[*] Updating package lists...")
    run_command(["sudo", "apt", "update"])

    print("[*] Installing Suricata and related tools...")
    run_command(["sudo", "apt", "install", "-y", "suricata", "jq", "python3-pip"])

    if not check_command_exists("suricata-update"):
        print("[*] Installing suricata-update via pip...")
        run_command(["sudo", "pip3", "install", "--upgrade", "suricata-update"])

    print("[*] Downloading additional rule sets...")
    run_command(["sudo", "suricata-update", "--install-rules"])

    print("[*] Updating Suricata rules...")
    run_command(["sudo", "suricata-update"])

    print("[*] Enabling Suricata to start on boot...")
    run_command(["sudo", "systemctl", "enable", "suricata"])

    print("[*] Installing other useful tools...")
    run_command([
        "sudo", "apt", "install", "-y",
        "iptables", "iptables-persistent", "ethtool", "tcpdump", "iftop"
    ])

    print("[*] Installing yq via snap...")
    run_command(["sudo", "snap", "install", "yq"])

    print("[*] Starting Suricata service...")
    run_command(["sudo", "systemctl", "start", "suricata"])

    print("[*] Suricata status:")
    run_command(["sudo", "systemctl", "status", "suricata", "--no-pager"])

    print("\n[*] Suricata logs will be written to /var/log/suricata/")
    print("[*] Fast log: /var/log/suricata/fast.log")
    print("[*] JSON log: /var/log/suricata/eve.json")
    print("\n[*] To monitor alerts in real time, run:")
    print("    sudo tail -f /var/log/suricata/fast.log")

if __name__ == "__main__":
    main()