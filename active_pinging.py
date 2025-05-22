#!/usr/bin/env python3

import subprocess
import ipaddress
import time
from pathlib import Path
from datetime import datetime

def read_allowed_ips(filename):
    try:
        with open(filename, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"[!] {filename} not found. Creating empty file.")
        Path(filename).touch()
        return set()

def ping(ip):
    try:

        result = subprocess.run(['ping', '-c', '1', '-W', '1', str(ip)], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def scan_network(network, allowed_ips):
    flags = []
    network = ipaddress.ip_network(network)
    
    print(f"[*] Scanning network {network}...")
    for ip in network.hosts():
        ip_str = str(ip)
        if ping(ip_str):
            print(f"[+] Host found: {ip_str}")
            if ip_str not in allowed_ips:
                print(f"[!] Unauthorized IP detected: {ip_str}")
                flags.append(ip_str)
    return flags

def main():

    base_dir = Path('/opt/active_pinging')
    allowed_ips_file = base_dir / "allowed_ips.txt"
    flags_file = base_dir / "flags.txt"
    network = "192.168.1.0/24"


    base_dir.mkdir(parents=True, exist_ok=True)

    while True:
        try:

            allowed_ips = read_allowed_ips(allowed_ips_file)
            

            unauthorized_ips = scan_network(network, allowed_ips)
            

            if unauthorized_ips:
                with open(flags_file, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for ip in unauthorized_ips:
                        f.write(f"{timestamp} - Unauthorized IP: {ip}\n")
                    f.flush() 

            time.sleep(150)
            
        except KeyboardInterrupt:
            print("\n[*] Scanning stopped by user")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()