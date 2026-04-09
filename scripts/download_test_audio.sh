#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST_PATH="${1:-${REPO_DIR}/assets/test_audio/es/manifest.json}"
OUTPUT_DIR="${2:-${REPO_DIR}/assets/test_audio/es}"

if [[ ! -f "${MANIFEST_PATH}" ]]; then
  echo "No existe el manifiesto: ${MANIFEST_PATH}" >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR}"

python3 - "${MANIFEST_PATH}" "${OUTPUT_DIR}" <<'PY'
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

manifest_path = Path(sys.argv[1])
output_dir = Path(sys.argv[2])

items = json.loads(manifest_path.read_text(encoding="utf-8"))

for item in items:
    target = output_dir / item["filename"]
    if target.exists():
        print(f"[skip] {target.name}")
        continue

    print(f"[down] {target.name}")
    subprocess.run(
        [
            "curl",
            "-L",
            "--retry",
            "5",
            "--retry-delay",
            "2",
            "--user-agent",
            "UNLZ-INCLU-IA-audio-fetch/1.0",
            "--output",
            str(target),
            item["url"],
        ],
        check=True,
    )
    time.sleep(2)

print(f"[ok] audios listos en {output_dir}")
PY
