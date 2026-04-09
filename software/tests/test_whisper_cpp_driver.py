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
