# Guia Linux / Raspberry Pi

Objetivo: instalar y operar Inclu-IA en Linux, especialmente Raspberry Pi OS 64-bit.

Referencia completa de STT: [`configuracion_stt.md`](configuracion_stt.md).

Drivers recomendados en Linux/Raspberry:

- `simulator`: validar frontend/red sin STT real.
- `faster_whisper`: baseline Python para STT local.
- `whisper_cpp`: alternativa de baja latencia/tuning edge si `whisper.cpp` esta compilado.

## 1) Prerrequisitos

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-venv python3-pip avahi-daemon
```

Usar siempre `bash scripts/...`, no `sh scripts/...`.

## 2) Instalar backend

Desde la raiz del repo:

```bash
sudo bash scripts/install_backend.sh
```

El script instala dependencias del sistema, incluyendo:

- `ffmpeg`
- `python3-dev`
- `portaudio19-dev`
- herramientas de build para `whisper.cpp`

Tambien prepara `whisper.cpp` por defecto:

- compila `whisper-stream`;
- descarga el modelo GGML `base`;
- configura `INCLUIA_WCPP_BIN` y `INCLUIA_WCPP_MODEL` en `software/.env`.

Para omitir `whisper.cpp` en una instalacion rapida:

```bash
INCLUIA_SKIP_WCPP=1 sudo bash scripts/install_backend.sh
```

## 3) Configurar .env

```bash
cd /home/pi/UNLZ-INCLU-IA/software
cp .env.example .env
nano .env
```

Campos minimos:

- `INCLUIA_DRIVER=simulator|faster_whisper|whisper_cpp`
- `INCLUIA_AP_SSID`
- `INCLUIA_AP_URL`

## 4) Diagnostico estricto de faster-whisper

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json
```

Para validar tambien carga/descarga del modelo:

```bash
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json --load-model
```

## 5) Preparar whisper.cpp manualmente

```bash
cd /home/pi/UNLZ-INCLU-IA
bash scripts/download_models.sh base /home/pi/whisper.cpp
```

Si se usa otra ruta, configurar:

- `INCLUIA_WCPP_BIN`
- `INCLUIA_WCPP_MODEL`

Ejemplo:

```bash
export INCLUIA_WCPP_BIN=/home/pi/whisper.cpp/build/bin/whisper-stream
export INCLUIA_WCPP_MODEL=/home/pi/whisper.cpp/models/ggml-base.bin
```

## 6) Levantar servidor manual

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
python server.py --driver faster_whisper
```

Para `whisper_cpp`:

```bash
python server.py --driver whisper_cpp
```

Para simulador:

```bash
python server.py --driver simulator
```

Desde el menu ⚙️ de la webapp se puede cambiar entre `simulator`, `faster_whisper`
y `whisper_cpp`, ajustar parametros basicos y aplicar sin editar archivos. Esos cambios
son de runtime; para dejarlos permanentes, copiar los valores a `software/.env`.

Para documentacion detallada de parametros, API y persistencia, ver
[`configuracion_stt.md`](configuracion_stt.md).

## 7) Levantar servicio systemd

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now inclu-ia.service
sudo systemctl status inclu-ia.service
```

Logs:

```bash
journalctl -u inclu-ia.service -f
```

## 8) Validar acceso desde celulares

Conectar al AP configurado y abrir:

- `http://192.168.4.1:5000`
- `http://inclu-ia.local:5000` si mDNS resuelve

## 9) Audio y microfono

Listar dispositivos:

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
python tools/list_audio_devices.py
```

Validar ALSA:

```bash
arecord -l
arecord -D plughw:1,0 -f S16_LE -r 48000 -c 1 -d 5 /tmp/test-mic.wav
```

Si el adaptador USB requiere una frecuencia especifica, definir:

```bash
export INCLUIA_AUDIO_SAMPLE_RATE=48000
```
