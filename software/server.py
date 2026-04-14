from __future__ import annotations

import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional fallback only
    load_dotenv = None

from incluia.app import create_server
from incluia.config import AppConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inclu-IA captions server")
    parser.add_argument("--host", help="Host bind")
    parser.add_argument("--port", type=int, help="Port bind")
    parser.add_argument(
        "--driver",
        choices=["simulator", "faster_whisper", "whisper_cpp"],
        help="Transcriber driver",
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    return parser.parse_args()


def main() -> None:
    if load_dotenv is not None:
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(env_path)

    args = parse_args()
    cfg = AppConfig.from_env()

    if args.host:
        cfg.host = args.host
    if args.port:
        cfg.port = args.port
    if args.driver:
        cfg.driver = args.driver
    if args.debug:
        cfg.debug = True

    app, socketio, cfg = create_server(cfg)
    socketio.run(
        app,
        host=cfg.host,
        port=cfg.port,
        debug=cfg.debug,
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    main()
