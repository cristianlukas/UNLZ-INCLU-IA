#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-${REPO_DIR}/assets/models/vosk}"
VERSION="${2:-vosk-model-small-es-0.42}"

mkdir -p "${OUTPUT_DIR}"

ZIP_PATH="${OUTPUT_DIR}/${VERSION}.zip"
MODEL_DIR="${OUTPUT_DIR}/${VERSION}"

if [[ ! -f "${ZIP_PATH}" ]]; then
  curl -L \
    --retry 5 \
    --retry-delay 2 \
    --user-agent "UNLZ-INCLU-IA-vosk-fetch/1.0" \
    --output "${ZIP_PATH}" \
    "https://alphacephei.com/vosk/models/${VERSION}.zip"
fi

if [[ ! -d "${MODEL_DIR}" ]]; then
  python3 - "${ZIP_PATH}" "${OUTPUT_DIR}" <<'PY'
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1])
output_dir = Path(sys.argv[2])

with zipfile.ZipFile(zip_path) as archive:
    archive.extractall(output_dir)
PY
fi

echo "[ok] modelo listo en ${MODEL_DIR}"
