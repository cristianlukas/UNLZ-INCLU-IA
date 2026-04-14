from __future__ import annotations

import json


def main() -> None:
    import pyaudio

    audio = pyaudio.PyAudio()
    try:
        items: list[dict] = []
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
        print(json.dumps(items, indent=2, ensure_ascii=False))
    finally:
        audio.terminate()


if __name__ == "__main__":
    main()
