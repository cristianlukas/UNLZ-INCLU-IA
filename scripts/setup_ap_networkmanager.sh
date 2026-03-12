#!/usr/bin/env bash
set -euo pipefail

SSID="${1:-Inclu-IA_Classroom}"
PASSWORD="${2:-CambiarEstaClave123!}"
IFACE="${3:-wlan0}"
CON_NAME="IncluIA-AP"

if [[ ${#PASSWORD} -lt 8 ]]; then
  echo "La password WPA2 debe tener al menos 8 caracteres"
  exit 1
fi

echo "[1/4] Verificando NetworkManager"
sudo systemctl enable --now NetworkManager

echo "[2/4] Recreando conexion AP ${CON_NAME}"
sudo nmcli connection delete "${CON_NAME}" >/dev/null 2>&1 || true
sudo nmcli connection add type wifi ifname "${IFACE}" con-name "${CON_NAME}" autoconnect yes ssid "${SSID}"

echo "[3/4] Configurando AP"
sudo nmcli connection modify "${CON_NAME}" \
  802-11-wireless.mode ap \
  802-11-wireless.band bg \
  ipv4.method shared \
  ipv4.addresses 192.168.4.1/24 \
  ipv6.method ignore \
  wifi-sec.key-mgmt wpa-psk \
  wifi-sec.psk "${PASSWORD}"

echo "[4/4] Levantando AP"
sudo nmcli connection up "${CON_NAME}"

cat <<EOF
AP listo.
SSID: ${SSID}
IFACE: ${IFACE}
Gateway AP: 192.168.4.1
URL sugerida: http://192.168.4.1:5000
EOF