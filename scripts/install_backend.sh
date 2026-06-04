#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SW_DIR="${REPO_DIR}/software"
RUN_USER="${SUDO_USER:-${USER}}"
SERVICE_SRC="${REPO_DIR}/deploy/inclu-ia.service"
SERVICE_TMP="$(mktemp)"
# Perfil de hardware: pi4 -> base-q5_1, pi5 -> small-q5_1.
# INCLUIA_WCPP_MODEL_SIZE explicito gana sobre el perfil.
PI_PROFILE="${INCLUIA_PI_PROFILE:-}"
case "${PI_PROFILE}" in
  pi4) PROFILE_MODEL="base-q5_1" ;;
  pi5) PROFILE_MODEL="small-q5_1" ;;
  *)   PROFILE_MODEL="base" ;;
esac
WHISPER_CPP_MODEL="${INCLUIA_WCPP_MODEL_SIZE:-${PROFILE_MODEL}}"
WHISPER_CPP_DIR="${INCLUIA_WCPP_DIR:-/home/${RUN_USER}/whisper.cpp}"

set_env_value() {
  local key="$1"
  local value="$2"
  local env_file="${SW_DIR}/.env"

  if grep -q "^${key}=" "${env_file}"; then
    sed -i "s|^${key}=.*|${key}=${value}|g" "${env_file}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${env_file}"
  fi
}

echo "[0/8] Instalando dependencias del sistema"
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

echo "[1/8] Creando entorno virtual"
python3 -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/8] Actualizando pip"
pip install --upgrade pip

echo "[3/8] Instalando dependencias Python"
pip install -r requirements.txt

echo "[4/8] Preparando archivo .env"
if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
fi

echo "[5/8] Preparando whisper.cpp"
if [[ "${INCLUIA_SKIP_WCPP:-0}" == "1" ]]; then
  echo "Saltando whisper.cpp por INCLUIA_SKIP_WCPP=1"
else
  sudo -u "${RUN_USER}" bash "${REPO_DIR}/scripts/download_models.sh" \
    "${WHISPER_CPP_MODEL}" \
    "${WHISPER_CPP_DIR}"
  set_env_value "INCLUIA_WCPP_BIN" "${WHISPER_CPP_DIR}/build/bin/whisper-stream"
  set_env_value "INCLUIA_WCPP_MODEL" "${WHISPER_CPP_DIR}/models/ggml-${WHISPER_CPP_MODEL}.bin"
fi

echo "[6/8] Generando unit file"
sed \
  -e "s|__RUN_USER__|${RUN_USER}|g" \
  -e "s|__REPO_DIR__|${REPO_DIR}|g" \
  "${SERVICE_SRC}" > "${SERVICE_TMP}"

echo "[7/8] Instalando unit file"
sudo cp "${SERVICE_TMP}" /etc/systemd/system/inclu-ia.service
rm -f "${SERVICE_TMP}"

echo "[8/8] Recargando systemd"
sudo systemctl daemon-reload

echo "Instalacion finalizada. Edita software/.env y luego ejecuta:"
echo "  sudo systemctl enable --now inclu-ia.service"
