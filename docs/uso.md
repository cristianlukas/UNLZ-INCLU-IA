# Uso diario

Guias por sistema operativo:

- Windows: [`docs/guia_windows.md`](guia_windows.md)
- Linux / Raspberry Pi: [`docs/guia_linux.md`](guia_linux.md)

## Inicio manual (sin systemd)

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
python server.py
```

Opciones:

```bash
python server.py --driver simulator --host 0.0.0.0 --port 5000
python server.py --driver faster_whisper
python server.py --driver whisper_cpp
```

## Inicio con systemd

```bash
sudo systemctl start inclu-ia.service
sudo systemctl restart inclu-ia.service
sudo systemctl stop inclu-ia.service
sudo systemctl status inclu-ia.service
```

Logs en vivo:

```bash
journalctl -u inclu-ia.service -f
```

## Endpoints utiles

- Health: `GET /_health`
- Config: `GET /api/config`
- Historial: `GET /api/history`
- Limpieza historial: `POST /api/clear`

## Flujo recomendado de clase

1. Encender Raspberry Pi.
2. Verificar AP arriba (`nmcli c show --active` o `ip a`).
3. Verificar servicio (`systemctl status`).
4. Conectar celulares al AP.
5. Abrir URL local y validar estado `Escuchando`.

## Notas de driver

- `simulator`: para desarrollo frontend y pruebas de red.
- `faster_whisper`: pipeline Python simple para MVP y pruebas locales en Windows.
- `whisper_cpp`: opcion para tuning de latencia en edge, principalmente Raspberry/Linux.
- Desde el menu ⚙️ de la webapp se puede cambiar el backend STT y parametros basicos en runtime.
- Los cambios hechos desde la webapp aplican al proceso actual; para dejarlos fijos, copiar valores a `.env`.

## Ajustes utiles de audio en Raspberry Pi

- `INCLUIA_AUDIO_DEVICE_INDEX`: indice de entrada para PyAudio.
- `INCLUIA_AUDIO_SAMPLE_RATE`: frecuencia del microfono para `faster_whisper` (si no se define, intenta usar la del dispositivo; algunos adaptadores USB requieren `48000`).
- `INCLUIA_FW_PHRASE_LIMIT_S`: duracion maxima de cada bloque escuchado.
- `INCLUIA_WCPP_STEP_MS` y `INCLUIA_WCPP_LENGTH_MS`: ventana y paso de `whisper.cpp`.
- `INCLUIA_SOCKET_TRANSPORT`: `polling` para AP inestable o `websocket` si queres priorizar baja sobrecarga.

## Diagnostico rapido de audio

Validar configuracion STT y dependencias del driver elegido:

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
python tools/check_stt_setup.py
```

Para diagnostico estricto sin volver al simulador:

```bash
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python server.py
```

En Windows PowerShell:

```powershell
cd .\Inclu-IA
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1
cd .\software
$env:INCLUIA_DRIVER="faster_whisper"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\tools\check_stt_setup.py
```

No usar `whisper_cpp` en Windows salvo que `whisper.cpp` este compilado y esten definidas:

- `INCLUIA_WCPP_BIN`
- `INCLUIA_WCPP_MODEL`

Listar dispositivos con PyAudio:

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
python tools/list_audio_devices.py
```

Validar el microfono con ALSA:

```bash
arecord -l
arecord -D plughw:1,0 -f S16_LE -r 48000 -c 1 -d 5 /tmp/test-mic.wav
```

## faster-whisper en modo streaming (captura continua)

Desde esta version, `faster_whisper` captura audio en background mientras transcribe chunks en una cola.

Variables utiles en `.env`:

- `INCLUIA_FW_PHRASE_LIMIT_S`: duracion del chunk (ej: 3 o 4).
- `INCLUIA_FW_QUEUE_MAX_CHUNKS`: tamano maximo de cola de chunks (default 8).

Recomendacion Pi 4:

- `INCLUIA_FW_PHRASE_LIMIT_S=3`
- `INCLUIA_FW_QUEUE_MAX_CHUNKS=6`

Si la cola se satura, se descartan chunks viejos para priorizar latencia de streaming.

Mensaje de diagnostico esperado cuando hay saturacion:

- `Audio en cola saturado: se descartaron chunks viejos para mantener streaming`

