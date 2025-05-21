import yaml
import sys
import os
import subprocess

CONFIG_PATH = "/etc/suricata/suricata.yaml"
BACKUP_PATH = CONFIG_PATH + ".bak"

def backup_config():
    if not os.path.exists(BACKUP_PATH):
        print("[*] Backing up original configuration...")
        os.system(f"sudo cp {CONFIG_PATH} {BACKUP_PATH}")

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def save_yaml(data, path):
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def update_eve_log(config):
    outputs = config.get("outputs", [])
    eve_found = False

    for out in outputs:
        if "eve-log" in out:
            eve = out["eve-log"]
            eve["enabled"] = True
            eve["filetype"] = "regular"
            eve["filename"] = "/var/log/suricata/eve.json"
            eve["types"] = ["dns", "http", "tls"]
            eve_found = True
            break

    if not eve_found:
        print("[*] No eve-log found, creating new entry...")
        outputs.append({
            "eve-log": {
                "enabled": True,
                "filetype": "regular",
                "filename": "/var/log/suricata/eve.json",
                "types": ["dns", "http", "tls"]
            }
        })

    config["outputs"] = outputs
    return config

def restart_suricata():
    print("[*] Restarting Suricata service...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "suricata"], check=True)
        print("[+] Suricata restarted successfully.")
    except subprocess.CalledProcessError as e:
        print("[-] Failed to restart Suricata. Please check the service status.")
        sys.exit(1)

def main():
    backup_config()

    try:
        config = load_yaml(CONFIG_PATH)
    except Exception as e:
        print(f"[-] Failed to load YAML: {e}")
        sys.exit(1)

    updated = update_eve_log(config)

    try:
        save_yaml(updated, CONFIG_PATH)
        print("[+] Suricata configuration updated successfully.")
    except Exception as e:
        print(f"[-] Failed to save YAML: {e}")
        sys.exit(1)

    restart_suricata()

if __name__ == "__main__":
    main()
