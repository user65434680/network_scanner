#!/usr/bin/env python3

import json
import time
from collections import defaultdict

LOG_FILE = "/var/log/suricata/eve.json"
visited_by_ip = defaultdict(set)

def parse_log_line(line):
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return

    src_ip = entry.get("src_ip")
    if not src_ip:
        return

    if entry.get("event_type") == "dns":
        rrname = entry.get("dns", {}).get("rrname")
        if rrname:
            visited_by_ip[src_ip].add(rrname)

    elif entry.get("event_type") == "http":
        host = entry.get("http", {}).get("hostname")
        url = entry.get("http", {}).get("url")
        if host:
            visited_by_ip[src_ip].add(f"http://{host}{url or ''}")

    elif entry.get("event_type") == "tls":
        sni = entry.get("tls", {}).get("sni")
        if sni:
            visited_by_ip[src_ip].add(sni)

def follow_file(file):
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def main():
    print("[*] Monitoring Suricata logs... (updates every 10 seconds)\n")
    with open(LOG_FILE, "r") as f:
        log_lines = follow_file(f)
        last_print = time.time()

        for line in log_lines:
            parse_log_line(line)

            if time.time() - last_print >= 10:
                print("\n--- Websites Visited by Internal IP ---\n")
                for ip, sites in visited_by_ip.items():
                    print(f"{ip}:")
                    for site in sorted(sites):
                        print(f"  - {site}")
                    print()
                last_print = time.time()

if __name__ == "__main__":
    main()
