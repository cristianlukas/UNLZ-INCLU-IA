#!/usr/bin/env bash
set -euo pipefail

# Modelos validos para Inclu-IA (multilingues, se fuerza espanol con -l es).
# No usar variantes *.en: son solo ingles.
ALLOWED_MODELS=("base" "base-q5_1" "small" "small-q5_1")

# Perfil de hardware -> modelo recomendado por defecto.
#   pi4 -> base-q5_1 (comandos de voz, menor RAM/CPU)
#   pi5 -> small-q5_1 (dictado/calidad, mas headroom)
PI_PROFILE="${INCLUIA_PI_PROFILE:-}"

default_model_for_profile() {
  case "${1}" in
    pi4) echo "base-q5_1" ;;
    pi5) echo "small-q5_1" ;;
    *) echo "" ;;
  esac
}

# Resolucion del modelo:
#   1) argumento explicito ($1)
#   2) default segun INCLUIA_PI_PROFILE
#   3) base
PROFILE_DEFAULT="$(default_model_for_profile "${PI_PROFILE}")"
MODEL="${1:-${PROFILE_DEFAULT:-base}}"
WHISPER_CPP_DIR="${2:-/home/pi/whisper.cpp}"
BUILD_JOBS="${BUILD_JOBS:-2}"
BUILD_ALL="${INCLUIA_WCPP_BUILD_ALL:-0}"

is_allowed_model() {
  local candidate="$1"
  for m in "${ALLOWED_MODELS[@]}"; do
    [[ "${m}" == "${candidate}" ]] && return 0
  done
  return 1
}

if ! is_allowed_model "${MODEL}"; then
  echo "ERROR: modelo '${MODEL}' no permitido." >&2
  echo "Validos: ${ALLOWED_MODELS[*]}" >&2
  echo "Perfiles: INCLUIA_PI_PROFILE=pi4 -> base-q5_1, INCLUIA_PI_PROFILE=pi5 -> small-q5_1" >&2
  exit 1
fi

echo "Perfil hardware: ${PI_PROFILE:-(sin perfil)}"
echo "Modelo solicitado: ${MODEL}"

echo "[1/4] Preparando whisper.cpp"
if [[ ! -d "${WHISPER_CPP_DIR}" ]]; then
  git clone https://github.com/ggml-org/whisper.cpp "${WHISPER_CPP_DIR}"
fi

cd "${WHISPER_CPP_DIR}"

echo "[2/4] Compilando binarios"
cmake -S . -B build -DWHISPER_SDL2=ON
if [[ "${BUILD_ALL}" == "1" ]]; then
  cmake --build build -j"${BUILD_JOBS}"
else
  cmake --build build --target whisper-stream -j"${BUILD_JOBS}"
fi

echo "[3/4] Descargando modelo ggml-${MODEL}.bin"
./models/download-ggml-model.sh "${MODEL}"

echo "[4/4] Recordatorio faster-whisper"
printf '%s\n' \
  "Si vas a usar faster-whisper, la primera corrida descarga modelo automaticamente." \
  "Para preparar cache offline, ejecuta server.py una vez con INCLUIA_DRIVER=faster_whisper."
