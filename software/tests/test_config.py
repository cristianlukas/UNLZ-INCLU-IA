from incluia.config import AppConfig


def test_config_defaults() -> None:
    cfg = AppConfig.from_env()
    assert cfg.port == 5000
    assert cfg.driver
    assert cfg.history_size >= 20
    assert cfg.faster_sample_rate == 16000


def test_config_sample_rate_from_env(monkeypatch) -> None:
    monkeypatch.setenv("INCLUIA_AUDIO_SAMPLE_RATE", "48000")

    cfg = AppConfig.from_env()

    assert cfg.faster_sample_rate == 48000
