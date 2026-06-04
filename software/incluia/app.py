from __future__ import annotations

from collections import deque
import logging
from pathlib import Path
from threading import Event, Lock
from typing import Any

import os
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

from .config import AppConfig
from .events import CaptionEvent, StatusEvent, now_ms
from .transcribers import build_transcriber
from .transcribers.simulator import SimulatorTranscriber


logger = logging.getLogger(__name__)


DRIVER_CHOICES = {"simulator", "faster_whisper", "whisper_cpp"}


def _config_payload(cfg: AppConfig, runtime: dict[str, Any]) -> dict[str, Any]:
    return {
        "driver": runtime["driver"],
        "active_source": runtime["active_source"],
        "ap_ssid": cfg.ap_ssid,
        "ap_url": cfg.ap_url,
        "history_size": cfg.history_size,
        "socket_transport": cfg.socket_transport,
        "status": runtime["status"],
        "fallback_to_simulator": cfg.fallback_to_simulator,
        "last_error": runtime["last_error"],
        "stt": {
            "driver": cfg.driver,
            "driver_options": sorted(DRIVER_CHOICES),
            "faster_model_size": cfg.faster_model_size,
            "faster_compute_type": cfg.faster_compute_type,
            "faster_language": cfg.faster_language,
            "faster_phrase_time_limit_s": cfg.faster_phrase_time_limit_s,
            "faster_vad_filter": cfg.faster_vad_filter,
            "faster_queue_max_chunks": cfg.faster_queue_max_chunks,
            "whisper_cpp_threads": cfg.whisper_cpp_threads,
            "whisper_cpp_step_ms": cfg.whisper_cpp_step_ms,
            "whisper_cpp_length_ms": cfg.whisper_cpp_length_ms,
            "whisper_cpp_vad_threshold": cfg.whisper_cpp_vad_threshold,
        },
    }


def _as_positive_int(value: Any, current: int, minimum: int = 1) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return current
    return max(minimum, parsed)


def _as_bool_value(value: Any, current: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return current


def _apply_config_patch(cfg: AppConfig, data: dict[str, Any]) -> None:
    driver = str(data.get("driver", cfg.driver)).strip()
    if driver not in DRIVER_CHOICES:
        raise ValueError(
            f"Driver invalido: {driver}. Usa simulator, faster_whisper o whisper_cpp."
        )

    cfg.driver = driver
    cfg.fallback_to_simulator = _as_bool_value(
        data.get("fallback_to_simulator"), cfg.fallback_to_simulator
    )
    cfg.faster_model_size = str(data.get("faster_model_size", cfg.faster_model_size)).strip()
    cfg.faster_compute_type = str(
        data.get("faster_compute_type", cfg.faster_compute_type)
    ).strip()
    cfg.faster_language = str(data.get("faster_language", cfg.faster_language)).strip()
    cfg.faster_phrase_time_limit_s = _as_positive_int(
        data.get("faster_phrase_time_limit_s"), cfg.faster_phrase_time_limit_s
    )
    cfg.faster_queue_max_chunks = _as_positive_int(
        data.get("faster_queue_max_chunks"), cfg.faster_queue_max_chunks
    )
    cfg.faster_vad_filter = _as_bool_value(
        data.get("faster_vad_filter"), cfg.faster_vad_filter
    )
    cfg.whisper_cpp_threads = _as_positive_int(
        data.get("whisper_cpp_threads"), cfg.whisper_cpp_threads
    )
    cfg.whisper_cpp_step_ms = _as_positive_int(
        data.get("whisper_cpp_step_ms"), cfg.whisper_cpp_step_ms, minimum=100
    )
    cfg.whisper_cpp_length_ms = _as_positive_int(
        data.get("whisper_cpp_length_ms"), cfg.whisper_cpp_length_ms, minimum=100
    )
    try:
        cfg.whisper_cpp_vad_threshold = float(
            data.get("whisper_cpp_vad_threshold", cfg.whisper_cpp_vad_threshold)
        )
    except (TypeError, ValueError):
        pass


def create_server(config: AppConfig | None = None) -> tuple[Flask, SocketIO, AppConfig]:
    cfg = config or AppConfig.from_env()

    root_dir = Path(__file__).resolve().parents[2]
    template_dir = root_dir / "web" / "templates"
    static_dir = root_dir / "web" / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
    )
    app.config["SECRET_KEY"] = "inclu-ia-dev"

    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        logger=False,
        engineio_logger=False,
        ping_timeout=30,
        ping_interval=20,
    )

    history: deque[dict[str, Any]] = deque(maxlen=max(20, cfg.history_size))
    runtime: dict[str, Any] = {
        "driver": cfg.driver,
        "active_source": cfg.driver,
        "status": StatusEvent(state="idle", detail="Inicializando").to_dict(),
        "last_error": None,
        "started": False,
    }

    stop_event_ref: dict[str, Event] = {"current": Event()}
    start_lock = Lock()

    def emit_status(event: StatusEvent) -> None:
        payload = event.to_dict()
        runtime["status"] = payload
        socketio.emit("status", payload)

    def emit_caption(event: CaptionEvent) -> None:
        payload = event.to_dict()
        if payload.get("is_final"):
            history.append(payload)
        socketio.emit("caption", payload)

    def run_transcriber() -> None:
        local_stop_event = stop_event_ref["current"]
        try:
            transcriber = build_transcriber(cfg)
            runtime["active_source"] = transcriber.source_name
            transcriber.run(local_stop_event, emit_caption, emit_status)
        except Exception as exc:
            runtime["last_error"] = {
                "type": type(exc).__name__,
                "detail": str(exc),
                "driver": cfg.driver,
            }
            logger.exception("Transcriber driver failed: %s", cfg.driver)
            emit_status(StatusEvent(state="error", detail=f"Driver fallo: {exc}"))

            should_fallback = cfg.fallback_to_simulator and cfg.driver != "simulator"
            if not should_fallback or local_stop_event.is_set():
                return

            emit_status(StatusEvent(state="idle", detail="Fallback a simulador"))
            runtime["active_source"] = "simulator"
            simulator = SimulatorTranscriber(
                interval_s=cfg.simulator_interval_s,
                lines=cfg.simulator_lines,
            )
            simulator.run(local_stop_event, emit_caption, emit_status)

    def ensure_background_started() -> None:
        with start_lock:
            if runtime["started"]:
                return
            runtime["started"] = True
            socketio.start_background_task(run_transcriber)

    def restart_transcriber() -> None:
        with start_lock:
            stop_event_ref["current"].set()
            stop_event_ref["current"] = Event()
            runtime["driver"] = cfg.driver
            runtime["active_source"] = cfg.driver
            runtime["last_error"] = None
            runtime["status"] = StatusEvent(
                state="idle", detail=f"Reiniciando driver {cfg.driver}"
            ).to_dict()
            runtime["started"] = True
            socketio.emit("config", _config_payload(cfg, runtime))
            socketio.emit("status", runtime["status"])
            socketio.start_background_task(run_transcriber)

    @app.before_request
    def _start_once() -> None:
        ensure_background_started()

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.get("/_health")
    def health() -> Any:
        return jsonify(
            {
                "ok": True,
                "driver": runtime["driver"],
                "active_source": runtime["active_source"],
                "status": runtime["status"],
                "fallback_to_simulator": cfg.fallback_to_simulator,
                "last_error": runtime["last_error"],
                "history_items": len(history),
                "t_server_ms": now_ms(),
            }
        )

    @app.get("/api/config")
    def get_config() -> Any:
        return jsonify(_config_payload(cfg, runtime))

    @app.post("/api/config")
    def update_config() -> Any:
        data = request.get_json(silent=True) or {}
        try:
            _apply_config_patch(cfg, data)
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400

        restart_transcriber()
        return jsonify({"ok": True, "config": _config_payload(cfg, runtime)})

    @app.get("/api/history")
    def get_history() -> Any:
        return jsonify({"items": list(history), "t_server_ms": now_ms()})

    @app.post("/api/clear")
    def clear_history() -> Any:
        history.clear()
        payload = {"t_server_ms": now_ms()}
        socketio.emit("history_cleared", payload)
        return jsonify(payload)

    @socketio.on("connect")
    def on_connect() -> None:
        ensure_background_started()
        socketio.emit("status", runtime["status"], to=request.sid)
        socketio.emit("history", {"items": list(history)}, to=request.sid)

    @socketio.on("clear_history")
    def on_clear_history() -> None:
        history.clear()
        socketio.emit("history_cleared", {"t_server_ms": now_ms()})
        
    return app, socketio, cfg
