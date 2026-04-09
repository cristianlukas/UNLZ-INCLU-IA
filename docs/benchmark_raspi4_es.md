# Benchmark en Espanol para Raspberry Pi 4

Objetivo: comparar `faster-whisper` con audios repetibles en espanol antes de seguir afinando captura por microfono.

## Preparacion en Windows 11

Desde la raiz del repo:

```powershell
python -m venv software\.venv
software\.venv\Scripts\python -m pip install --upgrade pip
software\.venv\Scripts\python -m pip install -r software\requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\download_test_audio.ps1
software\.venv\Scripts\python .\software\tools\benchmark_faster_whisper.py
```

Salida esperada:

- audios en `assets/test_audio/es`
- resultados en `software/benchmark_results/faster_whisper_es_results.json`

## Ejecucion sugerida en Raspberry Pi 4

Equipo objetivo: Raspberry Pi 4 Model B 8GB con Raspberry Pi OS 64-bit.

Preparacion recomendada en la Pi:

```bash
cd /home/pi/Inclu-IA
sudo apt update
sudo apt install -y curl python3 python3-venv python3-pip ffmpeg
bash scripts/install_backend.sh
bash scripts/download_test_audio.sh
bash scripts/run_benchmark_raspi4_es.sh
```

Salida esperada en la Pi:

- audios en `assets/test_audio/es`
- benchmark en `software/benchmark_results/pi4_faster_whisper_es.json`

Si queres correrlo manualmente:

```bash
cd /home/pi/Inclu-IA/software
source .venv/bin/activate
python tools/benchmark_faster_whisper.py \
  --manifest ../assets/test_audio/es/manifest.json \
  --audio-dir ../assets/test_audio/es \
  --models tiny base small \
  --language es \
  --compute-type int8 \
  --output ./benchmark_results/pi4_faster_whisper_es.json
```

## Como leer los resultados

- `elapsed_seconds`: tiempo total de transcripcion.
- `audio_seconds`: duracion del archivo.
- `realtime_factor`: `elapsed_seconds / audio_seconds`.
- `expected_token_recall`: proporcion simple de palabras esperadas recuperadas.
- `matched_expected`: chequeo simple del texto esperado normalizado.

Interpretacion practica:

- `realtime_factor < 1.0`: mas rapido que tiempo real.
- `realtime_factor` cerca de `1.0`: usable con cuidado.
- `realtime_factor > 1.5`: dificil para subtitulado en vivo.

## Criterio recomendado para el becario

- Fijar idioma en espanol: `INCLUIA_FW_LANGUAGE=es`.
- Probar primero con archivos, no con microfono.
- Si `small` mejora texto pero supera tiempo real en Pi 4, no usarlo para vivo.
- Si el adaptador USB requiere 48000 Hz, definir `INCLUIA_AUDIO_SAMPLE_RATE=48000`.
- Una vez elegido el mejor modelo por archivo, recien ahi retomar pruebas con microfono.

## Referencia inicial tomada en Windows 11

Archivo de salida generado:

- `software/benchmark_results/faster_whisper_es_results.json`

Lectura rapida:

- `tiny`: muy rapido, pero mas errores en frases formales y nombres propios.
- `base`: casi tan rapido como `tiny` en esta PC y bastante mejor en el dialogo formal.
- `small`: mejora el dialogo claro, pero ya penaliza bastante mas en habla rapida rioplatense.

Esto no representa Raspberry Pi 4. Sirve solo como linea base para que el becario compare contra la Pi y vea cuanto cae el rendimiento real.

## Recomendacion inicial para Pi 4 Model B 8GB

- Empezar por `base`.
- Dejar `small` solo para comparativa, no como candidato inicial de tiempo real.
- Si `base` en Pi 4 queda por encima de tiempo real con microfono, bajar a `tiny`.
