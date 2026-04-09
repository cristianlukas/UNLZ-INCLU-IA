#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SW_DIR="${REPO_DIR}/software"
OUTPUT_PATH="${1:-${SW_DIR}/benchmark_results/pi4_faster_whisper_es.json}"

mkdir -p "${SW_DIR}/benchmark_results"

cd "${SW_DIR}"

if [[ ! -d ".venv" ]]; then
  echo "Falta entorno virtual en ${SW_DIR}/.venv" >&2
  echo "Ejecuta primero: bash scripts/install_backend.sh" >&2
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

python tools/benchmark_faster_whisper.py \
  --manifest ../assets/test_audio/es/manifest.json \
  --audio-dir ../assets/test_audio/es \
  --models tiny base small \
  --language es \
  --compute-type int8 \
  --output "${OUTPUT_PATH}"
