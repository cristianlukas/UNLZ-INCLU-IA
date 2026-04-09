from __future__ import annotations

import os
import tempfile
from threading import Event

from ..events import CaptionEvent, StatusEvent
from .base import CaptionCallback, StatusCallback, Transcriber


class FasterWhisperTranscriber(Transcriber):
    source_name = "faster_whisper"

    def __init__(
        self,
        model_size: str,
        compute_type: str,
        language: str,
        phrase_time_limit_s: int,
        vad_filter: bool,
        device_index: int | None,
        sample_rate: int,
    ) -> None:
        self.model_size = model_size
        self.compute_type = compute_type
        self.language = language
        self.phrase_time_limit_s = phrase_time_limit_s
        self.vad_filter = vad_filter
        self.device_index = device_index
        self.sample_rate = sample_rate

    def run(
        self,
        stop_event: Event,
        on_caption: CaptionCallback,
        on_status: StatusCallback,
    ) -> None:
        try:
            import speech_recognition as sr
            from faster_whisper import WhisperModel
        except ImportError as exc:
            on_status(StatusEvent(state="error", detail=f"Dependencia faltante: {exc}"))
            raise RuntimeError("Missing dependencies for faster_whisper driver") from exc

        on_status(
            StatusEvent(
                state="idle",
                detail=f"Cargando modelo {self.model_size} ({self.compute_type})",
            )
        )

        model = WhisperModel(
            self.model_size,
            device="cpu",
            compute_type=self.compute_type,
        )

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True

        with sr.Microphone(
            sample_rate=self.sample_rate,
            device_index=self.device_index,
        ) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            on_status(
                StatusEvent(
                    state="listening",
                    detail=f"Microfono listo ({self.sample_rate} Hz)",
                )
            )

            while not stop_event.is_set():
                try:
                    audio = recognizer.listen(
                        source,
                        timeout=1,
                        phrase_time_limit=self.phrase_time_limit_s,
                    )
                except sr.WaitTimeoutError:
                    continue
                except Exception as exc:
                    on_status(StatusEvent(state="error", detail=f"Audio: {exc}"))
                    continue

                tmp_path = ""
                try:
                    on_status(StatusEvent(state="transcribing", detail="Procesando audio"))

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                        tmp.write(audio.get_wav_data())
                        tmp_path = tmp.name

                    segments, _ = model.transcribe(
                        tmp_path,
                        language=self.language,
                        vad_filter=self.vad_filter,
                        beam_size=1,
                        best_of=1,
                        condition_on_previous_text=False,
                    )

                    partial = ""
                    first_ms: int | None = None
                    last_ms: int | None = None

                    for segment in segments:
                        seg_text = segment.text.strip()
                        if not seg_text:
                            continue

                        partial = f"{partial} {seg_text}".strip()
                        if first_ms is None:
                            first_ms = int(segment.start * 1000)
                        last_ms = int(segment.end * 1000)

                        on_caption(
                            CaptionEvent(
                                text=partial,
                                is_final=False,
                                source=self.source_name,
                                t0_ms=first_ms,
                                t1_ms=last_ms,
                            )
                        )

                    if partial:
                        on_caption(
                            CaptionEvent(
                                text=partial,
                                is_final=True,
                                source=self.source_name,
                                t0_ms=first_ms,
                                t1_ms=last_ms,
                            )
                        )
                        on_status(StatusEvent(state="listening", detail="Esperando audio"))
                    else:
                        on_status(StatusEvent(state="listening", detail="Sin voz detectada"))

                except Exception as exc:
                    on_status(StatusEvent(state="error", detail=f"Transcripcion: {exc}"))
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
