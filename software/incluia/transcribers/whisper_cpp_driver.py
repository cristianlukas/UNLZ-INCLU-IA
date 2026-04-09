from __future__ import annotations

import os
import re
import subprocess
import time
from threading import Event

from ..events import CaptionEvent, StatusEvent
from .base import CaptionCallback, StatusCallback, Transcriber


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
TIMESTAMP_RE = re.compile(r"^\s*\[[^\]]+\]\s*(.+)$")
NOISE_PATTERNS = (
    re.compile(r"^(?:main|system_info|whisper_|wav_|audio_|capture_)\s*:?", re.IGNORECASE),
    re.compile(r"^(?:processing|listening|init(?:ializ\w*)?|loaded)\b", re.IGNORECASE),
    re.compile(r"^(?:n_threads|n_processors|language)\s*=", re.IGNORECASE),
)


def _extract_caption_text(raw_line: str) -> str | None:
    clean = ANSI_RE.sub("", raw_line).strip()
    if not clean:
        return None

    match = TIMESTAMP_RE.match(clean)
    text = match.group(1).strip() if match else clean
    if not text:
        return None

    for pattern in NOISE_PATTERNS:
        if pattern.match(text):
            return None

    if text.lower().startswith("error"):
        return text

    if not match and ":" in text and len(text.split()) <= 4:
        return None

    return text


class WhisperCppTranscriber(Transcriber):
    source_name = "whisper_cpp"

    def __init__(
        self,
        binary_path: str,
        model_path: str,
        threads: int,
        step_ms: int,
        length_ms: int,
        vad_threshold: float,
        language: str,
    ) -> None:
        self.binary_path = binary_path
        self.model_path = model_path
        self.threads = threads
        self.step_ms = step_ms
        self.length_ms = length_ms
        self.vad_threshold = vad_threshold
        self.language = language

    def run(
        self,
        stop_event: Event,
        on_caption: CaptionCallback,
        on_status: StatusCallback,
    ) -> None:
        if not os.path.exists(self.binary_path):
            detail = f"No existe binario: {self.binary_path}"
            on_status(StatusEvent(state="error", detail=detail))
            raise FileNotFoundError(detail)

        if not os.path.exists(self.model_path):
            detail = f"No existe modelo: {self.model_path}"
            on_status(StatusEvent(state="error", detail=detail))
            raise FileNotFoundError(detail)

        cmd = [
            self.binary_path,
            "-m",
            self.model_path,
            "--language",
            self.language,
            "--threads",
            str(self.threads),
            "--step",
            str(self.step_ms),
            "--length",
            str(self.length_ms),
            "-vth",
            str(self.vad_threshold),
        ]

        on_status(StatusEvent(state="idle", detail="Iniciando whisper.cpp"))

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        last_text = ""
        try:
            on_status(StatusEvent(state="listening", detail="Escuchando microfono"))
            while not stop_event.is_set():
                if process.poll() is not None:
                    break

                assert process.stdout is not None
                line = process.stdout.readline()
                if not line:
                    time.sleep(0.05)
                    continue

                text = _extract_caption_text(line)
                if not text:
                    continue

                if text.lower().startswith("error"):
                    on_status(StatusEvent(state="error", detail=text))
                    continue

                if text == last_text:
                    continue

                last_text = text
                on_status(StatusEvent(state="transcribing", detail="Procesando voz"))
                on_caption(
                    CaptionEvent(
                        text=text,
                        is_final=True,
                        source=self.source_name,
                    )
                )
                on_status(StatusEvent(state="listening", detail="Esperando voz"))
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
