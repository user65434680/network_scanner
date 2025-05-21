#!/usr/bin/env python3

import json
import time
from collections import defaultdict
from datetime import datetime

LOG_FILE = "/var/log/suricata/eve.json"
LOG_OUTPUT_FILE = "/opt/network_scan/logged_connections.txt"
visited_by_ip = defaultdict(list)

def current_time():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def parse_log_line(line):
    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        return

    src_ip = entry.get("src_ip")
    dest_ip = entry.get("dest_ip")
    timestamp = entry.get("timestamp", current_time())
    event_type = entry.get("event_type")

    if not src_ip:
        return

    if event_type == "dns":
        dns_entry = entry.get("dns", {})
        rrname = dns_entry.get("rrname")
        answers = dns_entry.get("answers", [])

        resolved_ips = [ans.get("rdata") for ans in answers if ans.get("type") == "A"]
        if rrname:
            visited_by_ip[src_ip].append({
                "type": "DNS",
                "domain": rrname,
                "resolved_ips": resolved_ips,
                "timestamp": timestamp
            })

    elif event_type == "http":
        http = entry.get("http", {})
        host = http.get("hostname")
        url = http.get("url", "")
        if host:
            visited_by_ip[src_ip].append({
                "type": "HTTP",
                "host": host,
                "url": url,
                "dest_ip": dest_ip,
                "timestamp": timestamp
            })

    elif event_type == "tls":
        tls = entry.get("tls", {})
        sni = tls.get("sni")
        if sni:
            visited_by_ip[src_ip].append({
                "type": "TLS",
                "sni": sni,
                "dest_ip": dest_ip,
                "timestamp": timestamp
            })

    elif event_type == "http":
        http = entry.get("http", {})
        host = http.get("hostname")
        url = http.get("url", "")
        full_url = f"http://{host}{url}" if host else url
        is_download = any(url.lower().endswith(ext) for ext in [
            ".exe", ".msi", ".zip", ".rar", ".tar", ".gz", ".deb", ".rpm", ".apk", ".bin", ".iso", ".7z"
        ])

        visited_by_ip[src_ip].append({
            "type": "HTTP",
            "host": host,
            "url": url,
            "dest_ip": dest_ip,
            "timestamp": timestamp,
            "download": is_download
        })

    elif event_type == "fileinfo":
        fileinfo = entry.get("fileinfo", {})
        filename = fileinfo.get("filename", "unknown")
        size = fileinfo.get("size")
        if filename and size:
            visited_by_ip[src_ip].append({
                "type": "FILE",
                "filename": filename,
                "size": size,
                "dest_ip": dest_ip,
                "timestamp": timestamp
            })


    elif event_type == "flow" and entry.get("app_proto") == "failed":
        visited_by_ip[src_ip].append({
            "type": "RAW",
            "dest_ip": dest_ip,
            "timestamp": timestamp
        })

def follow_file(file):
    file.seek(0, 2)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def format_connection(entry):
    t = entry["timestamp"]
    if entry["type"] == "DNS":
        resolved = f" -> {', '.join(entry['resolved_ips'])}" if entry['resolved_ips'] else ""
        return f"[{t}] DNS Query: {entry['domain']}{resolved}"
    elif entry["type"] == "HTTP":
        return f"[{t}] HTTP Access: http://{entry['host']}{entry['url']} (→ {entry['dest_ip']})"
    elif entry["type"] == "TLS":
        return f"[{t}] TLS SNI: {entry['sni']} (→ {entry['dest_ip']})"
    elif entry["type"] == "RAW":
        return f"[{t}] Direct IP connection: {entry['dest_ip']}"
    elif entry["type"] == "HTTP":
        marker = " (DOWNLOAD)" if entry.get("download") else ""
        return f"[{t}] HTTP Access: http://{entry['host']}{entry['url']} (→ {entry['dest_ip']}){marker}"
    elif entry["type"] == "FILE":
        size_mb = int(entry['size']) / (1024 * 1024)
        return f"[{t}] FILE Download: {entry['filename']} ({size_mb:.2f} MB) (→ {entry['dest_ip']})"

    return f"[{t}] Unknown entry"



def main():
    print("[*] Monitoring Suricata logs... (updates every 10 seconds)\n")
    
    unique_domains = defaultdict(set)
    
    with open(LOG_FILE, "r") as f:
        log_lines = follow_file(f)
        last_print = time.time()

        for line in log_lines:
            parse_log_line(line)

            if time.time() - last_print >= 10:
                output_lines = [f"\n--- {current_time()} - Connections Log ---\n"]
                
                for ip, entries in visited_by_ip.items():
                    current_domains = set()
                    filtered_entries = []
                    
                    for entry in entries:

                        if entry["type"] == "DNS":
                            domain = entry["domain"]
                            if domain not in unique_domains[ip]:
                                unique_domains[ip].add(domain)
                                filtered_entries.append(entry)
                        else:
                            filtered_entries.append(entry)
                    
                    if filtered_entries:
                        output_lines.append(f"{ip}:")
                        for e in filtered_entries:
                            output_lines.append(f"  - {format_connection(e)}")
                        output_lines.append("")

                output_text = "\n".join(output_lines)
                print(output_text)

                with open(LOG_OUTPUT_FILE, "a") as logfile:
                    logfile.write(output_text + "\n")
                    logfile.flush()

                last_print = time.time()

if __name__ == "__main__":
    main()
