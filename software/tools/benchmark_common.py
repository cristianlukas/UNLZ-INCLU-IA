from __future__ import annotations

import json
import re
import tempfile
import unicodedata
from pathlib import Path

import av


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def token_recall(expected_text: str, transcript: str) -> float | None:
    expected_tokens = normalize_text(expected_text).split()
    transcript_tokens = set(normalize_text(transcript).split())
    if not expected_tokens:
        return None

    hits = sum(1 for token in expected_tokens if token in transcript_tokens)
    return hits / len(expected_tokens)


def load_manifest(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def audio_duration_seconds(path: Path) -> float | None:
    with av.open(str(path)) as container:
        if container.duration is None:
            return None
        return float(container.duration / 1_000_000)


def convert_audio_to_temp_wav(path: Path, sample_rate: int = 16000) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()

    inp = av.open(str(path))
    out = av.open(tmp.name, mode="w")
    stream = out.add_stream("pcm_s16le", rate=sample_rate)
    stream.layout = "mono"
    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=sample_rate,
    )

    for frame in inp.decode(audio=0):
        converted = resampler.resample(frame)
        frames = converted if isinstance(converted, list) else [converted]
        for out_frame in frames:
            for packet in stream.encode(out_frame):
                out.mux(packet)

    for packet in stream.encode(None):
        out.mux(packet)

    out.close()
    inp.close()
    return Path(tmp.name)
