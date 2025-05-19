#!/bin/bash

set -e

echo "[+] Detecting network interfaces..."

interfaces=($(ls /sys/class/net | grep -v lo))

if [ "${#interfaces[@]}" -lt 2 ]; then
  echo "[-] Error: Less than 2 network interfaces found."
  exit 1
fi

if ! command -v nmcli >/dev/null 2>&1; then
    echo "[-] Error: nmcli is not installed. Please install NetworkManager."
    exit 1
fi


echo "[+] Enabling NetworkManager control over all interfaces..."

CONF_FILE="/etc/NetworkManager/NetworkManager.conf"

if [ ! -f "$CONF_FILE.bak" ]; then
    echo "[+] Backing up $CONF_FILE to $CONF_FILE.bak"
    sudo cp "$CONF_FILE" "$CONF_FILE.bak"
fi

if grep -q "^\[ifupdown\]" "$CONF_FILE"; then
    sudo sed -i '/^\[ifupdown\]/,/^\[/{s/^managed=.*/managed=true/}' "$CONF_FILE"
else
    echo -e "\n[ifupdown]\nmanaged=true" | sudo tee -a "$CONF_FILE" > /dev/null
fi

echo "[+] Restarting NetworkManager service..."
sudo systemctl restart NetworkManager

WAN_IF="${interfaces[0]}"
LAN_IF="${interfaces[1]}"

echo "[+] Using WAN interface: $WAN_IF"
echo "[+] Using LAN interface: $LAN_IF"

if nmcli device show "$WAN_IF" >/dev/null 2>&1; then
  echo "[+] Configuring WAN interface ($WAN_IF) to use DHCP with nmcli..."

  WAN_CON=$(nmcli -t -f NAME,DEVICE connection show --active | grep "$WAN_IF" | cut -d: -f1)
  if [ -z "$WAN_CON" ]; then
    WAN_CON=$(nmcli -t -f NAME,DEVICE connection show | grep "$WAN_IF" | cut -d: -f1)
    if [ -z "$WAN_CON" ]; then
      echo "[+] Creating new connection profile for $WAN_IF"
      nmcli connection add type ethernet ifname "$WAN_IF" con-name "WAN-$WAN_IF" autoconnect yes
      WAN_CON="WAN-$WAN_IF"
    fi
  fi

  nmcli connection modify "$WAN_CON" ipv4.method auto
  nmcli connection up "$WAN_CON"

else
  echo "[-] WAN interface $WAN_IF is not managed by NetworkManager"
fi

if nmcli device show "$LAN_IF" >/dev/null 2>&1; then
  echo "[+] Configuring LAN interface ($LAN_IF) with static IP 192.168.1.1/24 using nmcli..."

  LAN_CON=$(nmcli -t -f NAME,DEVICE connection show --active | grep "$LAN_IF" | cut -d: -f1)
  if [ -z "$LAN_CON" ]; then
    LAN_CON=$(nmcli -t -f NAME,DEVICE connection show | grep "$LAN_IF" | cut -d: -f1)
    if [ -z "$LAN_CON" ]; then
      echo "[+] Creating new connection profile for $LAN_IF"
      nmcli connection add type ethernet ifname "$LAN_IF" con-name "LAN-$LAN_IF" autoconnect yes
      LAN_CON="LAN-$LAN_IF"
    fi
  fi

  nmcli connection modify "$LAN_CON" ipv4.addresses 192.168.1.1/24
  nmcli connection modify "$LAN_CON" ipv4.gateway ""
  nmcli connection modify "$LAN_CON" ipv4.method manual
  nmcli connection down "$LAN_CON"
  nmcli connection up "$LAN_CON"

else
  echo "[-] LAN interface $LAN_IF is not managed by NetworkManager"
fi

echo "[+] Enabling IP forwarding..."
sudo sed -i '/^net.ipv4.ip_forward/d' /etc/sysctl.conf
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf > /dev/null
sudo sysctl -p

echo "[+] Setting up NAT and forwarding rules..."
sudo iptables -t nat -A POSTROUTING -o "$WAN_IF" -j MASQUERADE
sudo iptables -A FORWARD -i "$LAN_IF" -o "$WAN_IF" -j ACCEPT
sudo iptables -A FORWARD -i "$WAN_IF" -o "$LAN_IF" -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "[+] Installing iptables-persistent..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent

echo "[+] Saving iptables rules..."
sudo netfilter-persistent save

echo "[+] Creating systemd service for Suricata..."

sudo tee /etc/systemd/system/suricata.service > /dev/null <<EOF
[Unit]
Description=Suricata IDS/IPS
After=network.target

[Service]
ExecStart=/usr/bin/suricata -c /etc/suricata/suricata.yaml -i $WAN_IF -i $LAN_IF
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "[+] Reloading systemd daemon and enabling Suricata service..."
sudo systemctl daemon-reload
sudo systemctl enable suricata.service
sudo systemctl start suricata.service

echo "[+] Setup complete. Suricata is running on interfaces $WAN_IF and $LAN_IF and will auto-start on boot."