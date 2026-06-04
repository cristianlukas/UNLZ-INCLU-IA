# Guia Windows

Objetivo: levantar la webapp y validar STT local en Windows para pruebas de desarrollo.

Driver recomendado en Windows:

- `simulator`: validar frontend/red sin STT real.
- `faster_whisper`: validar transcripcion local.
- `whisper_cpp`: no recomendado salvo que `whisper.cpp` este compilado en Windows y se configuren rutas manuales.

## 1) Preparar backend

Desde la raiz del repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1
```

El script:

- instala `ffmpeg` con `winget` si falta;
- crea `software\.venv` si falta;
- instala `software\requirements.txt`;
- corre `tools\check_stt_setup.py` con `INCLUIA_DRIVER=faster_whisper`.

Si `ffmpeg` se instala en esta corrida, cerrar y abrir PowerShell antes de repetir el check.

## 2) Diagnostico estricto de faster-whisper

```powershell
cd .\software
$env:INCLUIA_DRIVER="faster_whisper"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\tools\check_stt_setup.py --json
```

Para validar tambien carga/descarga del modelo:

```powershell
.\.venv\Scripts\python .\tools\check_stt_setup.py --json --load-model
```

## 3) Levantar servidor con STT real

```powershell
cd .\software
$env:INCLUIA_DRIVER="faster_whisper"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\server.py --driver faster_whisper
```

Abrir:

- `http://127.0.0.1:5000`
- `http://<IP-LAN-DE-LA-PC>:5000` desde celulares en la misma red

## 4) Levantar servidor en simulador

```powershell
cd .\software
.\.venv\Scripts\python .\server.py --driver simulator
```

## 5) Sobre whisper_cpp en Windows

No usar `python server.py --driver whisper_cpp` en Windows salvo que existan:

- binario de `whisper.cpp` compilado para Windows;
- modelo GGML descargado;
- variables configuradas:
  - `INCLUIA_WCPP_BIN`
  - `INCLUIA_WCPP_MODEL`

Si esas rutas no existen, el server falla correctamente porque el driver no tiene binario/modelo para ejecutar.

## 6) Errores comunes

- `ffmpeg` falta: ejecutar `winget install Gyan.FFmpeg`, cerrar y abrir PowerShell.
- `PyAudio` falla: reinstalar dependencias con `.\.venv\Scripts\python -m pip install -r requirements.txt`.
- No hay microfono: correr `.\.venv\Scripts\python .\tools\list_audio_devices.py`.
- Vuelve al simulador: confirmar que `INCLUIA_FALLBACK_SIM=0` para ver el error real.
