from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from benchmark_common import (
    audio_duration_seconds,
    convert_audio_to_temp_wav,
    load_manifest,
    normalize_text,
    token_recall,
)


@dataclass(slots=True)
class BenchmarkRow:
    sample_id: str
    filename: str
    audio_seconds: float | None
    elapsed_seconds: float
    realtime_factor: float | None
    expected_token_recall: float | None
    matched_expected: bool | None
    transcript: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark reproducible de Moonshine con audios en espanol"
    )
    parser.add_argument(
        "--manifest",
        default="../assets/test_audio/es/manifest.json",
        help="Ruta al manifest JSON de audios",
    )
    parser.add_argument(
        "--audio-dir",
        default="../assets/test_audio/es",
        help="Directorio donde estan los audios",
    )
    parser.add_argument(
        "--language",
        default="es",
        help="Idioma fijo para Moonshine",
    )
    parser.add_argument(
        "--output",
        default="./benchmark_results/moonshine_es_results.json",
        help="Archivo JSON de salida",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    audio_dir = Path(args.audio_dir).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    from moonshine_voice import Transcriber, get_model_for_language
    from moonshine_voice.utils import load_wav_file

    manifest = load_manifest(manifest_path)
    model_path, model_arch = get_model_for_language(args.language)

    rows: list[BenchmarkRow] = []
    transcriber = Transcriber(model_path=model_path, model_arch=model_arch)
    try:
        for item in manifest:
            audio_path = audio_dir / item["filename"]
            if not audio_path.exists():
                print(f"[skip] falta {audio_path}")
                continue

            tmp_wav = convert_audio_to_temp_wav(audio_path)
            try:
                audio_data, sample_rate = load_wav_file(str(tmp_wav))
                started = time.perf_counter()
                transcript = transcriber.transcribe_without_streaming(audio_data, sample_rate)
                elapsed = time.perf_counter() - started
                text = " ".join(line.text.strip() for line in transcript.lines if line.text.strip())

                expected = item.get("expected_text")
                normalized_transcript = normalize_text(text)
                normalized_expected = normalize_text(expected) if expected else None
                matched_expected = None
                expected_recall = None
                if normalized_expected:
                    matched_expected = normalized_expected in normalized_transcript
                    expected_recall = token_recall(expected, text)

                audio_seconds = audio_duration_seconds(audio_path)
                rtf = None
                if audio_seconds and audio_seconds > 0:
                    rtf = elapsed / audio_seconds

                row = BenchmarkRow(
                    sample_id=item["id"],
                    filename=item["filename"],
                    audio_seconds=audio_seconds,
                    elapsed_seconds=elapsed,
                    realtime_factor=rtf,
                    expected_token_recall=expected_recall,
                    matched_expected=matched_expected,
                    transcript=text,
                )
                rows.append(row)
                print(
                    json.dumps(
                        {
                            "sample_id": row.sample_id,
                            "elapsed_seconds": round(row.elapsed_seconds, 3),
                            "realtime_factor": round(row.realtime_factor, 3)
                            if row.realtime_factor is not None
                            else None,
                            "expected_token_recall": round(row.expected_token_recall, 3)
                            if row.expected_token_recall is not None
                            else None,
                            "matched_expected": row.matched_expected,
                        },
                        ensure_ascii=False,
                    )
                )
            finally:
                os.unlink(tmp_wav)
    finally:
        transcriber.close()

    output = {
        "generated_at_epoch_s": time.time(),
        "language": args.language,
        "rows": [asdict(row) for row in rows],
    }
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] resultados en {output_path}")


if __name__ == "__main__":
    main()
