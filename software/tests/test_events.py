from incluia.events import CaptionEvent, StatusEvent


def test_status_event_has_timestamp() -> None:
    payload = StatusEvent(state="listening").to_dict()
    assert payload["state"] == "listening"
    assert payload["t_server_ms"] > 0


def test_caption_event_contract() -> None:
    payload = CaptionEvent(text="hola", is_final=True, source="simulator").to_dict()

    assert payload["id"]
    assert payload["text"] == "hola"
    assert payload["is_final"] is True
    assert payload["source"] == "simulator"
    assert payload["t_server_ms"] > 0