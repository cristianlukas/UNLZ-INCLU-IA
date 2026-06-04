from __future__ import annotations

from incluia.config import AppConfig
from tools import check_stt_setup
from tools.check_stt_setup import build_report


def test_check_stt_setup_reports_simulator(monkeypatch) -> None:
    monkeypatch.setenv("INCLUIA_DRIVER", "simulator")

    report = build_report(load_model=False)

    assert report["ok"] in {True, False}
    assert report["config"]["driver"] == "simulator"
    assert any(check["name"] == "simulator_driver" for check in report["checks"])


def test_check_stt_setup_recommends_ffmpeg_install(monkeypatch) -> None:
    monkeypatch.setattr(check_stt_setup.shutil, "which", lambda _name: None)
    monkeypatch.setattr(check_stt_setup.platform, "system", lambda: "Windows")

    status = check_stt_setup._ffmpeg_status()

    assert status["ok"] is False
    assert "winget install Gyan.FFmpeg" in status["recommendation"]


def test_check_stt_setup_recommends_whisper_cpp_setup(monkeypatch) -> None:
    monkeypatch.setattr(check_stt_setup.platform, "system", lambda: "Windows")
    cfg = AppConfig(
        driver="whisper_cpp",
        whisper_cpp_binary="./missing/whisper-stream.exe",
        whisper_cpp_model="./missing/ggml-base.bin",
    )

    status = check_stt_setup._whisper_cpp_status(cfg)

    assert status["binary_exists"] is False
    assert status["model_exists"] is False
    assert "INCLUIA_WCPP_BIN" in status["recommendation"]
    assert "faster_whisper" in status["recommendation"]
