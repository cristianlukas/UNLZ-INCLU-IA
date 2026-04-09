from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark reproducible de faster-whisper con audios en espanol"
    )
    parser.add_argument(
        "--manifest",
        default="../../assets/test_audio/es/manifest.json",
        help="Ruta al manifest JSON de audios",
    )
    parser.add_argument(
        "--audio-dir",
        default="../../assets/test_audio/es",
        help="Directorio donde estan los audios",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["tiny", "base", "small"],
        help="Modelos a probar",
    )
    parser.add_argument("--language", default="es", help="Idioma fijo para Whisper")
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Compute type para faster-whisper",
    )
    parser.add_argument(
        "--output",
        default="../benchmark_results/faster_whisper_es_results.json",
        help="Archivo JSON de salida",
    )
    return parser.parse_args()


def audio_duration_seconds(path: Path) -> float | None:
    try:
        import av
    except ImportError:
        return None

    with av.open(str(path)) as container:
        if container.duration is None:
            return None
        return float(container.duration / 1_000_000)


@dataclass(slots=True)
class BenchmarkRow:
    model: str
    sample_id: str
    filename: str
    audio_seconds: float | None
    elapsed_seconds: float
    realtime_factor: float | None
    expected_token_recall: float | None
    matched_expected: bool | None
    transcript: str


def load_manifest(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def token_recall(expected_text: str, transcript: str) -> float | None:
    expected_tokens = normalize_text(expected_text).split()
    transcript_tokens = set(normalize_text(transcript).split())
    if not expected_tokens:
        return None

    hits = sum(1 for token in expected_tokens if token in transcript_tokens)
    return hits / len(expected_tokens)


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest).resolve()
    audio_dir = Path(args.audio_dir).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    from faster_whisper import WhisperModel

    manifest = load_manifest(manifest_path)
    rows: list[BenchmarkRow] = []

    for model_name in args.models:
        print(f"[model] {model_name}")
        model = WhisperModel(
            model_name,
            device="cpu",
            compute_type=args.compute_type,
        )

        for item in manifest:
            audio_path = audio_dir / item["filename"]
            if not audio_path.exists():
                print(f"[skip] falta {audio_path}")
                continue

            started = time.perf_counter()
            segments, _ = model.transcribe(
                str(audio_path),
                language=args.language,
                vad_filter=True,
                beam_size=1,
                best_of=1,
                condition_on_previous_text=False,
            )
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
            elapsed = time.perf_counter() - started

            expected = item.get("expected_text")
            normalized_transcript = normalize_text(transcript)
            normalized_expected = normalize_text(expected) if expected else None
            matched_expected = None
            expected_recall = None
            if normalized_expected:
                matched_expected = normalized_expected in normalized_transcript
                expected_recall = token_recall(expected, transcript)

            audio_seconds = audio_duration_seconds(audio_path)
            rtf = None
            if audio_seconds and audio_seconds > 0:
                rtf = elapsed / audio_seconds

            row = BenchmarkRow(
                model=model_name,
                sample_id=item["id"],
                filename=item["filename"],
                audio_seconds=audio_seconds,
                elapsed_seconds=elapsed,
                realtime_factor=rtf,
                expected_token_recall=expected_recall,
                matched_expected=matched_expected,
                transcript=transcript,
            )
            rows.append(row)
            print(
                json.dumps(
                    {
                        "model": row.model,
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

    output = {
        "generated_at_epoch_s": time.time(),
        "language": args.language,
        "compute_type": args.compute_type,
        "rows": [asdict(row) for row in rows],
    }
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] resultados en {output_path}")


if __name__ == "__main__":
    main()
