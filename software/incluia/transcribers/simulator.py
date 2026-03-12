from __future__ import annotations

from threading import Event

from ..events import CaptionEvent, StatusEvent
from .base import CaptionCallback, StatusCallback, Transcriber


DEFAULT_LINES = [
    "Bienvenidos a Inclu-IA.",
    "Esta es una demo de subtitulado en tiempo real.",
    "El backend emite eventos por Socket.IO.",
    "El frontend muestra subtitulos con alto contraste.",
]


class SimulatorTranscriber(Transcriber):
    source_name = "simulator"

    def __init__(self, interval_s: float = 1.2, lines: list[str] | None = None) -> None:
        self.interval_s = max(interval_s, 0.2)
        self.lines = lines or DEFAULT_LINES

    def run(
        self,
        stop_event: Event,
        on_caption: CaptionCallback,
        on_status: StatusCallback,
    ) -> None:
        on_status(StatusEvent(state="listening", detail="Simulador activo"))

        idx = 0
        while not stop_event.is_set():
            text = self.lines[idx % len(self.lines)]
            words = text.split()

            on_status(StatusEvent(state="transcribing", detail="Generando subtitulo"))
            for offset in range(1, len(words) + 1):
                if stop_event.wait(self.interval_s / max(len(words), 1)):
                    return
                partial = " ".join(words[:offset])
                on_caption(
                    CaptionEvent(
                        text=partial,
                        is_final=False,
                        source=self.source_name,
                    )
                )

            on_caption(
                CaptionEvent(
                    text=text,
                    is_final=True,
                    source=self.source_name,
                )
            )
            on_status(StatusEvent(state="listening", detail="Esperando audio"))

            idx += 1
            stop_event.wait(0.15)