from incluia.transcribers import whisper_cpp_driver
from incluia.transcribers.whisper_cpp_driver import _extract_caption_text


def test_extract_caption_text_from_timestamped_line() -> None:
    text = _extract_caption_text("[00:00:00.000 --> 00:00:02.000] hola mundo")

    assert text == "hola mundo"


def test_extract_caption_text_ignores_init_noise() -> None:
    text = _extract_caption_text("\x1b[0mwhisper_init_state: loading model\x1b[0m")

    assert text is None


def test_extract_caption_text_ignores_short_log_lines() -> None:
    text = _extract_caption_text("main: processing samples")

    assert text is None


def test_missing_file_detail_on_windows_recommends_faster_whisper(monkeypatch) -> None:
    monkeypatch.setattr(whisper_cpp_driver.platform, "system", lambda: "Windows")

    detail = whisper_cpp_driver._missing_file_detail("binario", "./whisper-stream")

    assert "faster_whisper" in detail
    assert "INCLUIA_WCPP_BIN" in detail
