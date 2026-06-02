from __future__ import annotations

from tools.check_stt_setup import build_report


def test_check_stt_setup_reports_simulator(monkeypatch) -> None:
    monkeypatch.setenv("INCLUIA_DRIVER", "simulator")

    report = build_report(load_model=False)

    assert report["ok"] in {True, False}
    assert report["config"]["driver"] == "simulator"
    assert any(check["name"] == "simulator_driver" for check in report["checks"])
