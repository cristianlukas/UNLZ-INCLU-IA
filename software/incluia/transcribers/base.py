from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Event
from typing import Callable

from ..events import CaptionEvent, StatusEvent

CaptionCallback = Callable[[CaptionEvent], None]
StatusCallback = Callable[[StatusEvent], None]


class Transcriber(ABC):
    source_name = "unknown"

    @abstractmethod
    def run(
        self,
        stop_event: Event,
        on_caption: CaptionCallback,
        on_status: StatusCallback,
    ) -> None:
        """Block while transcribing until stop_event is set."""