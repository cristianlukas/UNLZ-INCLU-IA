#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-base}"
WHISPER_CPP_DIR="${2:-/home/pi/whisper.cpp}"

echo "Modelo solicitado: ${MODEL}"

echo "[1/4] Preparando whisper.cpp"
if [[ ! -d "${WHISPER_CPP_DIR}" ]]; then
  git clone https://github.com/ggml-org/whisper.cpp "${WHISPER_CPP_DIR}"
fi

cd "${WHISPER_CPP_DIR}"

echo "[2/4] Compilando binarios"
cmake -S . -B build -DWHISPER_SDL2=ON
cmake --build build -j

echo "[3/4] Descargando modelo ggml-${MODEL}.bin"
./models/download-ggml-model.sh "${MODEL}"

echo "[4/4] Recordatorio faster-whisper"
cat <<EOF
Si vas a usar faster-whisper, la primera corrida descarga modelo automaticamente.
Para preparar cache offline, ejecuta server.py una vez con INCLUIA_DRIVER=faster_whisper.
EOF