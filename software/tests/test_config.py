from incluia.config import AppConfig


def test_config_defaults() -> None:
    cfg = AppConfig.from_env()
    assert cfg.port == 5000
    assert cfg.driver
    assert cfg.history_size >= 20