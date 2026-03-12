#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SW_DIR="${REPO_DIR}/software"

cd "${SW_DIR}"

echo "[1/6] Creando entorno virtual"
python3 -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/6] Actualizando pip"
pip install --upgrade pip

echo "[3/6] Instalando dependencias"
pip install -r requirements.txt

echo "[4/6] Preparando archivo .env"
if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
fi

echo "[5/6] Instalando unit file"
sudo cp "${REPO_DIR}/deploy/inclu-ia.service" /etc/systemd/system/inclu-ia.service

echo "[6/6] Recargando systemd"
sudo systemctl daemon-reload

echo "Instalacion finalizada. Edita software/.env y luego ejecuta:"
echo "  sudo systemctl enable --now inclu-ia.service"