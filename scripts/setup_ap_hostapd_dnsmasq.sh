#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOSTAPD_SRC="${REPO_DIR}/software/config/hostapd.conf"
DNSMASQ_SRC="${REPO_DIR}/software/config/dnsmasq.conf"

echo "[1/6] Instalando paquetes"
sudo apt update
sudo apt install -y hostapd dnsmasq

echo "[2/6] Copiando configuraciones"
sudo cp "${HOSTAPD_SRC}" /etc/hostapd/hostapd.conf
sudo cp "${DNSMASQ_SRC}" /etc/dnsmasq.conf

echo "[3/6] Activando hostapd.conf"
if grep -q '^#DAEMON_CONF=' /etc/default/hostapd; then
  sudo sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
elif grep -q '^DAEMON_CONF=' /etc/default/hostapd; then
  sudo sed -i 's|^DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
else
  echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee -a /etc/default/hostapd >/dev/null
fi

echo "[4/6] Configurando IP estatica de wlan0"
if ! grep -q '^interface wlan0' /etc/dhcpcd.conf; then
  cat <<'EOF' | sudo tee -a /etc/dhcpcd.conf >/dev/null

interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOF
fi

echo "[5/6] Habilitando servicios"
sudo systemctl unmask hostapd
sudo systemctl enable hostapd dnsmasq

echo "[6/6] Reiniciando servicios"
sudo systemctl restart dhcpcd
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq

cat <<EOF
AP listo con hostapd + dnsmasq.
SSID: Inclu-IA_Classroom
Gateway AP: 192.168.4.1
URL sugerida: http://192.168.4.1:5000
EOF