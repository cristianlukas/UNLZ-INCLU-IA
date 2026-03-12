from __future__ import annotations

from dataclasses import asdict, dataclass
from time import time
from typing import Any
from uuid import uuid4


def now_ms() -> int:
    return int(time() * 1000)


@dataclass(slots=True)
class StatusEvent:
    state: str
    detail: str = ""
    t_server_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if not payload["t_server_ms"]:
            payload["t_server_ms"] = now_ms()
        return payload


@dataclass(slots=True)
class CaptionEvent:
    text: str
    is_final: bool
    source: str
    t0_ms: int | None = None
    t1_ms: int | None = None
    caption_id: str = ""
    t_server_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.caption_id or str(uuid4()),
            "text": self.text,
            "t0_ms": self.t0_ms,
            "t1_ms": self.t1_ms,
            "is_final": self.is_final,
            "source": self.source,
            "t_server_ms": self.t_server_ms or now_ms(),
        }
        return payload