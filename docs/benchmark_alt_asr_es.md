# Benchmark alternativo de ASR en espanol

Objetivo: comparar dos alternativas a Whisper para espanol:

- `Moonshine`
- `Vosk`

Contexto objetivo:

- Windows 11 para preparacion local
- Raspberry Pi 4 Model B 8GB para validacion real
- operacion offline

## Preparacion en Windows 11

Desde la raiz del repo:

```powershell
python -m venv software\.venv
software\.venv\Scripts\python -m pip install --upgrade pip
software\.venv\Scripts\python -m pip install -r software\requirements.txt
software\.venv\Scripts\python -m pip install -r software\requirements-alt-asr.txt
powershell -ExecutionPolicy Bypass -File .\scripts\download_test_audio.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\download_vosk_es_model.ps1
```

## Benchmark Moonshine en Windows 11

```powershell
software\.venv\Scripts\python .\software\tools\benchmark_moonshine.py
```

Salida:

- `software/benchmark_results/moonshine_es_results.json`

## Benchmark Vosk en Windows 11

```powershell
software\.venv\Scripts\python .\software\tools\benchmark_vosk.py
```

Salida:

- `software/benchmark_results/vosk_es_results.json`

## Preparacion en Raspberry Pi 4B 8GB

```bash
cd /home/pi/Inclu-IA
sudo apt update
sudo apt install -y curl python3 python3-venv python3-pip ffmpeg
bash scripts/install_backend.sh
source software/.venv/bin/activate
pip install -r software/requirements-alt-asr.txt
bash scripts/download_test_audio.sh
bash scripts/download_vosk_es_model.sh
```

## Benchmark Moonshine en Raspberry Pi

```bash
cd /home/pi/Inclu-IA/software
source .venv/bin/activate
python tools/benchmark_moonshine.py \
  --manifest ../assets/test_audio/es/manifest.json \
  --audio-dir ../assets/test_audio/es \
  --output ./benchmark_results/pi4_moonshine_es.json
```

## Benchmark Vosk en Raspberry Pi

```bash
cd /home/pi/Inclu-IA/software
source .venv/bin/activate
python tools/benchmark_vosk.py \
  --manifest ../assets/test_audio/es/manifest.json \
  --audio-dir ../assets/test_audio/es \
  --model-path ../assets/models/vosk/vosk-model-small-es-0.42 \
  --output ./benchmark_results/pi4_vosk_es.json
```

## Como interpretar

- `realtime_factor`: menor a `1.0` significa mas rapido que tiempo real.
- `expected_token_recall`: recuperacion simple de palabras esperadas.

Lectura sugerida:

- Si `Moonshine` logra mejor texto sin perder tiempo real, vale la pena probarlo con microfono.
- Si `Vosk` es claramente mas rapido pero transcribe peor, dejarlo como plan B de baja latencia.
- No reemplazar Whisper solo por velocidad: comparar tambien estabilidad y calidad de frases corridas.

## Referencia inicial tomada en Windows 11

Archivos generados:

- `software/benchmark_results/moonshine_es_results.json`
- `software/benchmark_results/vosk_es_results.json`
- `software/benchmark_results/faster_whisper_es_results.json`

Lectura rapida de esta PC:

- `faster-whisper base`: fue el mas rapido y balanceado de los probados.
- `Moonshine`: transcribio bastante bien los dialogos claros, pero en esta PC quedo bastante mas lento que `faster-whisper base`.
- `Vosk`: fue rapido en los dialogos claros, pero degrado mucho en la muestra corta rioplatense.

Conclusion practica para repetir en la Pi:

- priorizar `faster-whisper base` como baseline
- probar `Moonshine` como alternativa real a Whisper
- dejar `Vosk` como opcion de contingencia si la prioridad absoluta es latencia

## Nota de licencia

- `Moonshine` descarga modelo bajo su licencia comunitaria no comercial.
- `Vosk` usa modelo `vosk-model-small-es-0.42` con licencia Apache 2.0.
