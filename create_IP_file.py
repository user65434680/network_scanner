import os
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
projects_dir = os.path.join(parent_dir, 'projects')

if projects_dir not in sys.path:
    sys.path.insert(0, projects_dir)

from project_context import get_current_project_number

project_number = get_current_project_number()
custom_clients_path = os.path.join(projects_dir, project_number, 'custom_clients.ini')
inventory_path = os.path.join(parent_dir, 'inventory', 'inventory.ini')


ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')


def extract_ips_from_file(file_path):
    """Reads IPs from a file if it exists and returns a set of valid IPs."""
    ips = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                found_ips = ip_pattern.findall(line)
                for ip in found_ips:
                    if all(0 <= int(octet) <= 255 for octet in ip.split('.')):
                        ips.add(ip)
    except FileNotFoundError:
        pass
    return ips


def extract_ips_from_inventory():
    ips = extract_ips_from_file(custom_clients_path)

    if ips:
        print(f"Using IPs from: {custom_clients_path}")
    else:
        print(f"No valid IPs in {custom_clients_path}, falling back to inventory.ini")
        ips = extract_ips_from_file(inventory_path)

    if not ips:
        print("No IPs found in either file.")
        return

    output_file = '/opt/active_pinging/allowed_ips.txt'
    flags_file = '/opt/active_pinging/flags.txt'
    
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if os.path.exists(output_file):
            os.remove(output_file)
            print(f"Removed existing {output_file}")
        
        if os.path.exists(flags_file):
            os.remove(flags_file)
            print(f"Removed existing {flags_file}")

        with open(output_file, 'w') as f_out:
            for ip in sorted(ips):
                f_out.write(ip + '\n')
        print(f"Extracted {len(ips)} IPs to {output_file}")
    except PermissionError:
        print(f"Permission denied: cannot write to {output_file}")



if __name__ == '__main__':
    extract_ips_from_inventory()
