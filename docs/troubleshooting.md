# Troubleshooting

Guias por sistema operativo:

- Windows: [`docs/guia_windows.md`](guia_windows.md)
- Linux / Raspberry Pi: [`docs/guia_linux.md`](guia_linux.md)
- Configuracion STT: [`docs/configuracion_stt.md`](configuracion_stt.md)

## El servidor no arranca

- Revisar dependencias:

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
pip install -r requirements.txt
```

- Revisar logs:

```bash
journalctl -u inclu-ia.service -n 200 --no-pager
```

## Celulares no ven la web

- Verificar AP activo (`wlan0` con `192.168.4.1`).
- Verificar que backend escucha en `0.0.0.0:5000`.
- Probar desde la Pi: `curl http://127.0.0.1:5000/_health`.

## Estado queda en error

- Ver payload de `status.detail` en la UI.
- Ver `last_error` en `GET /_health`; incluye tipo de excepcion, detalle y driver.
- Si falla driver real y `INCLUIA_FALLBACK_SIM=1`, debe entrar a simulador.
- Si no queres fallback, poner `INCLUIA_FALLBACK_SIM=0` para diagnostico estricto.
- Desde la webapp, abrir `⚙️`, desactivar `Fallback simulador`, aplicar STT y leer el error real.

Diagnostico estricto recomendado:

```bash
cd /home/pi/UNLZ-INCLU-IA/software
source .venv/bin/activate
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python server.py
```

En Windows PowerShell:

```powershell
cd .\software
$env:INCLUIA_DRIVER="faster_whisper"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\tools\check_stt_setup.py
.\.venv\Scripts\python .\server.py
```

Si el check falla, guardar la salida de:

```bash
python tools/check_stt_setup.py --json
```

Usar `--load-model` solo cuando se quiera validar descarga/cache del modelo, porque puede tardar.

## faster-whisper no captura audio

- Revisar que el microfono este visible para ALSA/PyAudio.
- Definir `INCLUIA_AUDIO_DEVICE_INDEX` con un indice valido.
- Si el adaptador USB trabaja a otra frecuencia, definir `INCLUIA_AUDIO_SAMPLE_RATE` (por ejemplo `48000`).
- Si el backend falla al abrir el microfono, correr `python tools/list_audio_devices.py` y verificar `max_input_channels`.
- Si `arecord` solo funciona con un canal, usar `-c 1` en la prueba ALSA y fijar el `device_index` correcto en `.env`.
- Probar primero con microfono USB antes de Bluetooth.

## PyAudio falla al instalar

- En Raspberry Pi OS instalar primero:
  - `python3-dev`
  - `portaudio19-dev`
  - `ffmpeg`

## whisper.cpp tarda demasiado al compilar

- Instalar dependencias de build:
  - `build-essential`
  - `pkg-config`
  - `cmake`
  - `ninja-build`
- En Pi 4 usar `bash scripts/download_models.sh base /home/pi/whisper.cpp` para compilar solo `whisper-stream`.
- Si queres compilar todo el proyecto, usar `INCLUIA_WCPP_BUILD_ALL=1`.

## whisper.cpp falla por binario/modelo

- Verificar rutas:
  - `INCLUIA_WCPP_BIN`
  - `INCLUIA_WCPP_MODEL`
- Ejecutar `scripts/download_models.sh`.
- En Windows, ejecutar `powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1`.
- En Linux/Raspberry, ejecutar `sudo bash scripts/install_backend.sh` o `bash scripts/download_models.sh base /home/pi/whisper.cpp`.

Check estricto:

```bash
INCLUIA_DRIVER=whisper_cpp INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json
```

## Latencia alta

- Medir primero con archivos mediante `tools/benchmark_faster_whisper.py`; no mezclar rendimiento del modelo con problemas de microfono.
- Reducir modelo (`tiny` o `base`).
- En Raspberry Pi 4, `small` suele mejorar precision pero aumentar mucho la demora; no asumir tiempo real.
- En `faster_whisper`, bajar `INCLUIA_FW_PHRASE_LIMIT_S`.
- En `whisper_cpp`, ajustar `INCLUIA_WCPP_STEP_MS` y `INCLUIA_WCPP_LENGTH_MS`.
- Validar VAD activo (`INCLUIA_FW_VAD=1` o `-vth` en whisper.cpp).
- Desde la UI, probar primero `simulator`, luego `faster_whisper`, luego `whisper_cpp`; no comparar STT si la red/UI todavia no esta estable.

## Seguridad WiFi

- No usar TKIP.
- Cambiar password por una fuerte antes de demo publica.
## Console muestra GET /socket.io/socket.io.js 400

- Causa tipica: cliente JS de Socket.IO no compatible o path legado.
- En este repo el cliente correcto es local: /static/vendor/socket.io.min.js.
- Si el navegador mantiene cache viejo, forzar recarga con Ctrl+F5.

## En celular por AP la UI se congela

- Dejar `INCLUIA_SOCKET_TRANSPORT=polling` en `.env`.
- Reiniciar el servicio y probar de nuevo.
- Si el navegador movil mantiene assets viejos, cerrar la PWA o limpiar cache del sitio.

