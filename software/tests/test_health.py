from __future__ import annotations

from incluia.app import create_server
from incluia.config import AppConfig


def test_health_endpoint_reports_runtime_status() -> None:
    cfg = AppConfig(
        driver="simulator",
        simulator_interval_s=999.0,
        history_size=20,
    )
    app, _socketio, _cfg = create_server(cfg)
    with app.app_context():
        response = app.view_functions["health"]()
    payload = response.get_json()

    assert payload["ok"] is True
    assert payload["driver"] == "simulator"
    assert payload["active_source"] in {"simulator", "faster_whisper", "whisper_cpp"}
    assert payload["status"]["state"] in {"idle", "listening", "transcribing", "error"}
    assert payload["fallback_to_simulator"] is True
    assert payload["last_error"] is None


def test_config_endpoint_reports_stt_settings() -> None:
    cfg = AppConfig(driver="simulator", simulator_interval_s=999.0)
    app, _socketio, _cfg = create_server(cfg)

    with app.app_context():
        response = app.view_functions["get_config"]()
    payload = response.get_json()

    assert payload["stt"]["driver"] == "simulator"
    assert "faster_whisper" in payload["stt"]["driver_options"]
    assert "whisper_cpp" in payload["stt"]["driver_options"]


def test_config_endpoint_rejects_invalid_driver() -> None:
    cfg = AppConfig(driver="simulator", simulator_interval_s=999.0)
    app, _socketio, _cfg = create_server(cfg)

    with app.test_request_context(json={"driver": "bad_driver"}):
      response, status_code = app.view_functions["update_config"]()

    assert status_code == 400
    assert response.get_json()["ok"] is False
