#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SW_DIR="${REPO_DIR}/software"
RUN_USER="${SUDO_USER:-${USER}}"
SERVICE_SRC="${REPO_DIR}/deploy/inclu-ia.service"
SERVICE_TMP="$(mktemp)"

echo "[0/7] Instalando dependencias del sistema"
sudo apt update
sudo apt install -y \
  git \
  build-essential \
  pkg-config \
  cmake \
  ninja-build \
  ffmpeg \
  python3-dev \
  portaudio19-dev

cd "${SW_DIR}"

echo "[1/7] Creando entorno virtual"
python3 -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/7] Actualizando pip"
pip install --upgrade pip

echo "[3/7] Instalando dependencias"
pip install -r requirements.txt

echo "[4/7] Preparando archivo .env"
if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
fi

echo "[5/7] Generando unit file"
sed \
  -e "s|__RUN_USER__|${RUN_USER}|g" \
  -e "s|__REPO_DIR__|${REPO_DIR}|g" \
  "${SERVICE_SRC}" > "${SERVICE_TMP}"

echo "[6/7] Instalando unit file"
sudo cp "${SERVICE_TMP}" /etc/systemd/system/inclu-ia.service
rm -f "${SERVICE_TMP}"

echo "[7/7] Recargando systemd"
sudo systemctl daemon-reload

echo "Instalacion finalizada. Edita software/.env y luego ejecuta:"
echo "  sudo systemctl enable --now inclu-ia.service"
