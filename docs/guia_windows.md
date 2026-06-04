# Guia Windows

Objetivo: levantar la webapp y validar STT local en Windows para pruebas de desarrollo.

Drivers disponibles en Windows:

- `simulator`: validar frontend/red sin STT real.
- `faster_whisper`: validar transcripcion local.
- `whisper_cpp`: transcripcion por binario `whisper.cpp`, compilado por el instalador.

## 1) Preparar backend

Desde la raiz del repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1
```

El script:

- instala `ffmpeg` con `winget` si falta;
- crea `software\.venv` si falta;
- instala `software\requirements.txt`;
- clona/actualiza `whisper.cpp`;
- compila `whisper-stream.exe`;
- descarga el modelo GGML `base`;
- configura `INCLUIA_WCPP_BIN` y `INCLUIA_WCPP_MODEL` en `software\.env`;
- corre `tools\check_stt_setup.py` para `faster_whisper` y `whisper_cpp`.

Si `ffmpeg` se instala en esta corrida, cerrar y abrir PowerShell antes de repetir el check.
Si se instalan Visual Studio Build Tools, puede ser necesario cerrar y abrir PowerShell antes de compilar.

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

Con `faster_whisper`:

```powershell
cd .\software
$env:INCLUIA_DRIVER="faster_whisper"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\server.py --driver faster_whisper
```

Con `whisper_cpp`:

```powershell
cd .\software
$env:INCLUIA_DRIVER="whisper_cpp"
$env:INCLUIA_FALLBACK_SIM="0"
.\.venv\Scripts\python .\tools\check_stt_setup.py --json
.\.venv\Scripts\python .\server.py --driver whisper_cpp
```

Abrir:

- `http://127.0.0.1:5000`
- `http://<IP-LAN-DE-LA-PC>:5000` desde celulares en la misma red

Desde el menu ⚙️ de la webapp se puede cambiar entre `simulator`, `faster_whisper`
y `whisper_cpp`, ajustar parametros basicos y aplicar sin editar archivos. Esos cambios
son de runtime; para dejarlos permanentes, copiar los valores a `software\.env`.

## 4) Levantar servidor en simulador

```powershell
cd .\software
.\.venv\Scripts\python .\server.py --driver simulator
```

## 5) Errores comunes

- `ffmpeg` falta: ejecutar `winget install Gyan.FFmpeg`, cerrar y abrir PowerShell.
- `cmake` o `git` faltan: repetir `scripts\install_windows_backend.ps1`; el script intenta instalarlos con `winget`.
- `whisper-stream.exe` no compila: instalar Visual Studio Build Tools con workload C++ y repetir el script.
- `PyAudio` falla: reinstalar dependencias con `.\.venv\Scripts\python -m pip install -r requirements.txt`.
- No hay microfono: correr `.\.venv\Scripts\python .\tools\list_audio_devices.py`.
- Vuelve al simulador: confirmar que `INCLUIA_FALLBACK_SIM=0` para ver el error real.
