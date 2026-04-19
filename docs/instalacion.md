# Instalacion

## 0) Prerrequisitos

- Raspberry Pi OS 64-bit actualizado.
- Usuario con sudo.
- Repo clonado en `/home/pi/UNLZ-INCLU-IA`.
- En Linux, ejecutar scripts del repo con `bash scripts/...`, no con `sh scripts/...`.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip avahi-daemon
```

## 1) Configurar red AP (sin internet)

### Opcion recomendada: NetworkManager

```bash
cd /home/pi/UNLZ-INCLU-IA
sudo bash scripts/setup_ap_networkmanager.sh "Inclu-IA_Classroom" "TuClaveSegura123"
```

### Opcion alternativa: hostapd + dnsmasq

```bash
cd /home/pi/UNLZ-INCLU-IA
sudo bash scripts/setup_ap_hostapd_dnsmasq.sh
```

## 2) Instalar backend

```bash
cd /home/pi/UNLZ-INCLU-IA
sudo bash scripts/install_backend.sh
```

## 3) Configurar variables

```bash
cd /home/pi/UNLZ-INCLU-IA/software
cp .env.example .env
nano .env
```

Campos minimos:

- `INCLUIA_DRIVER=simulator|faster_whisper|whisper_cpp`
- `INCLUIA_AP_SSID`
- `INCLUIA_AP_URL`

## 4) (Opcional) Descargar modelos whisper.cpp

```bash
cd /home/pi/UNLZ-INCLU-IA
bash scripts/download_models.sh base /home/pi/whisper.cpp
```

## 4.1) (Opcional) Descargar audios de prueba en espanol

```bash
cd /home/pi/UNLZ-INCLU-IA
bash scripts/download_test_audio.sh
```

## 5) Activar servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now inclu-ia.service
sudo systemctl status inclu-ia.service
```

## 6) Acceso desde celulares

Conectar al SSID configurado y abrir:

- `http://192.168.4.1:5000`
- o `http://inclu-ia.local:5000` (si mDNS resuelve)

## Seguridad minima

- Cambiar `wpa_passphrase` por una clave fuerte.
- Mantener WPA2-CCMP (sin TKIP).
- No ejecutar backend en `debug` en produccion.
