from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


SOFTWARE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = SOFTWARE_DIR.parent
if str(SOFTWARE_DIR) not in sys.path:
    sys.path.insert(0, str(SOFTWARE_DIR))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional fallback only
    load_dotenv = None

from incluia.config import AppConfig


def _is_windows() -> bool:
    return platform.system().lower() == "windows"


def _ffmpeg_install_hint() -> str:
    if _is_windows():
        return "Instalar ffmpeg con: winget install Gyan.FFmpeg; despues cerrar y abrir PowerShell."
    return "Instalar ffmpeg con: sudo apt install -y ffmpeg"


def _whisper_cpp_install_hint() -> str:
    if _is_windows():
        return (
            "whisper_cpp requiere compilar whisper.cpp y configurar "
            "INCLUIA_WCPP_BIN/INCLUIA_WCPP_MODEL. "
            "Para pruebas en Windows usar faster_whisper salvo que se prepare whisper.cpp manualmente."
        )
    return (
        "Preparar whisper.cpp con: bash scripts/download_models.sh base /home/pi/whisper.cpp "
        "y configurar INCLUIA_WCPP_BIN/INCLUIA_WCPP_MODEL si se usa otra ruta."
    )


def _module_status(module_name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(module_name)
    return {
        "module": module_name,
        "installed": spec is not None,
        "origin": spec.origin if spec is not None else None,
    }


def _audio_devices() -> dict[str, Any]:
    try:
        import pyaudio
    except ImportError as exc:
        return {"ok": False, "error": f"PyAudio no instalado: {exc}", "items": []}

    audio = pyaudio.PyAudio()
    try:
        items: list[dict[str, Any]] = []
        for index in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(index)
            items.append(
                {
                    "index": index,
                    "name": info.get("name"),
                    "max_input_channels": info.get("maxInputChannels"),
                    "default_sample_rate": int(info.get("defaultSampleRate", 0)),
                }
            )
        input_items = [
            item for item in items if int(item.get("max_input_channels") or 0) > 0
        ]
        return {"ok": bool(input_items), "error": None, "items": items}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "items": []}
    finally:
        audio.terminate()


def _load_faster_whisper_model(cfg: AppConfig) -> dict[str, Any]:
    try:
        from faster_whisper import WhisperModel

        WhisperModel(
            cfg.faster_model_size,
            device="cpu",
            compute_type=cfg.faster_compute_type,
        )
        return {"ok": True, "error": None}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _candidate_paths(path_value: str) -> list[Path]:
    path = Path(path_value)
    if path.is_absolute():
        return [path]
    return [Path.cwd() / path, SOFTWARE_DIR / path, REPO_DIR / path]


def _existing_path(path_value: str) -> Path | None:
    for candidate in _candidate_paths(path_value):
        if candidate.exists():
            return candidate
    return None


def _ffmpeg_status() -> dict[str, Any]:
    ffmpeg_path = shutil.which("ffmpeg")
    status: dict[str, Any] = {
        "name": "ffmpeg",
        "ok": ffmpeg_path is not None,
        "path": ffmpeg_path,
    }
    if ffmpeg_path is None:
        status["recommendation"] = _ffmpeg_install_hint()
    return status


def _whisper_cpp_status(cfg: AppConfig) -> dict[str, Any]:
    binary_path = Path(cfg.whisper_cpp_binary)
    model_path = Path(cfg.whisper_cpp_model)
    resolved_binary_path = _existing_path(cfg.whisper_cpp_binary)
    resolved_model_path = _existing_path(cfg.whisper_cpp_model)
    ok = resolved_binary_path is not None and resolved_model_path is not None
    status: dict[str, Any] = {
        "binary_path": str(binary_path),
        "binary_exists": resolved_binary_path is not None,
        "resolved_binary_path": str(resolved_binary_path) if resolved_binary_path else None,
        "model_path": str(model_path),
        "model_exists": resolved_model_path is not None,
        "resolved_model_path": str(resolved_model_path) if resolved_model_path else None,
    }
    if not ok:
        status["recommendation"] = _whisper_cpp_install_hint()
    return {
        **status,
    }


def _checks_for_driver(cfg: AppConfig, load_model: bool) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    if cfg.driver == "faster_whisper":
        modules = [
            _module_status("faster_whisper"),
            _module_status("speech_recognition"),
            _module_status("pyaudio"),
        ]
        checks.append(
            {
                "name": "faster_whisper_dependencies",
                "ok": all(m["installed"] for m in modules),
                "modules": modules,
            }
        )
        checks.append({"name": "audio_devices", **_audio_devices()})
        if load_model:
            checks.append(
                {"name": "faster_whisper_model_load", **_load_faster_whisper_model(cfg)}
            )

    if cfg.driver == "whisper_cpp":
        status = _whisper_cpp_status(cfg)
        checks.append(
            {
                "name": "whisper_cpp_files",
                "ok": status["binary_exists"] and status["model_exists"],
                **status,
            }
        )

    if cfg.driver == "simulator":
        checks.append({"name": "simulator_driver", "ok": True})

    return checks


def build_report(load_model: bool) -> dict[str, Any]:
    if load_dotenv is not None:
        load_dotenv(SOFTWARE_DIR / ".env")

    cfg = AppConfig.from_env()
    checks = [
        {
            "name": "python",
            "ok": True,
            "version": sys.version.split()[0],
            "executable": sys.executable,
        },
        {"name": "platform", "ok": True, "value": platform.platform()},
        _ffmpeg_status(),
        {"name": "fallback_mode", "ok": True, "enabled": cfg.fallback_to_simulator},
        *_checks_for_driver(cfg, load_model),
    ]
    recommendations = [
        check["recommendation"]
        for check in checks
        if not check.get("ok") and check.get("recommendation")
    ]

    return {
        "ok": all(check.get("ok") for check in checks),
        "config": asdict(cfg),
        "checks": checks,
        "recommendations": recommendations,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Diagnostico de instalacion STT de Inclu-IA"
    )
    parser.add_argument(
        "--load-model",
        action="store_true",
        help="Carga el modelo faster-whisper para validar descarga/cache. Puede tardar.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Imprime el reporte completo en JSON"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = build_report(load_model=args.load_model)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"STT setup: {'OK' if report['ok'] else 'CON OBSERVACIONES'}")
        print(f"Driver: {report['config']['driver']}")
        fallback = "ON" if report["config"]["fallback_to_simulator"] else "OFF"
        print(f"Fallback simulador: {fallback}")
        for check in report["checks"]:
            state = "OK" if check.get("ok") else "FAIL"
            print(f"- {state}: {check['name']}")
            if check.get("error"):
                print(f"  error: {check['error']}")
            if check.get("recommendation"):
                print(f"  recomendacion: {check['recommendation']}")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
