# Configuracion STT

Esta guia documenta como instalar, elegir, modificar y diagnosticar los backends de transcripcion de Inclu-IA.

Backends disponibles:

- `simulator`: subtitulos simulados para validar UI, red y dispositivos.
- `faster_whisper`: STT local via Python.
- `whisper_cpp`: STT local via binario `whisper.cpp`.

## 1) Instalacion de backends

### Windows

Desde la raiz del repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1
```

El instalador prepara ambos backends reales:

- instala/valida `ffmpeg`;
- crea `software\.venv`;
- instala dependencias Python para `faster_whisper`;
- instala/valida `git`, `cmake` y Visual Studio Build Tools;
- clona/actualiza `whisper.cpp`;
- compila `whisper-stream.exe`;
- descarga `ggml-base.bin`;
- escribe `INCLUIA_WCPP_BIN` y `INCLUIA_WCPP_MODEL` en `software\.env`;
- corre `tools\check_stt_setup.py` para `faster_whisper` y `whisper_cpp`.

Opciones:

```powershell
# No intenta instalar ffmpeg
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1 -SkipFfmpeg

# No compila whisper.cpp
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1 -SkipWhisperCpp

# Usa otro modelo GGML
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows_backend.ps1 -WhisperCppModel tiny
```

### Linux / Raspberry Pi

Desde la raiz del repo:

```bash
sudo bash scripts/install_backend.sh
```

El instalador prepara:

- dependencias del sistema;
- entorno Python y dependencias de `faster_whisper`;
- `whisper.cpp`;
- modelo GGML `base`;
- rutas `INCLUIA_WCPP_BIN` y `INCLUIA_WCPP_MODEL` en `software/.env`.

Opciones:

```bash
# Omitir whisper.cpp
INCLUIA_SKIP_WCPP=1 sudo bash scripts/install_backend.sh

# Usar otro modelo
INCLUIA_WCPP_MODEL_SIZE=tiny sudo bash scripts/install_backend.sh

# Usar otra ruta para whisper.cpp
INCLUIA_WCPP_DIR=/opt/whisper.cpp sudo bash scripts/install_backend.sh
```

## 2) Cambiar backend desde la webapp

Abrir la webapp y entrar al menu `⚙️`.

Controles disponibles:

- `Backend STT`: `simulator`, `faster_whisper`, `whisper_cpp`.
- `Modelo FW`: modelo de `faster_whisper` (`tiny`, `base`, `small`).
- `Chunk FW (s)`: duracion maxima del chunk de audio en `faster_whisper`.
- `WCPP step (ms)`: avance de ventana para `whisper_cpp`.
- `WCPP length (ms)`: longitud de ventana para `whisper_cpp`.
- `Fallback simulador`: si esta activo, un fallo del driver real entra a simulador.
- `Aplicar STT`: guarda la configuracion runtime y reinicia el transcriber.

Importante:

- Los cambios desde la webapp son de runtime.
- No modifican automaticamente `software/.env`.
- Si se reinicia el proceso, vuelve a usar `.env` y argumentos CLI.

## 3) Persistir cambios en `.env`

Para hacer permanente una configuracion probada desde la UI, copiar los valores a `software/.env`.

Ejemplo `faster_whisper`:

```env
INCLUIA_DRIVER=faster_whisper
INCLUIA_FALLBACK_SIM=0
INCLUIA_FW_MODEL=base
INCLUIA_FW_COMPUTE_TYPE=int8
INCLUIA_FW_LANGUAGE=es
INCLUIA_FW_PHRASE_LIMIT_S=3
INCLUIA_FW_QUEUE_MAX_CHUNKS=6
```

Ejemplo `whisper_cpp`:

```env
INCLUIA_DRIVER=whisper_cpp
INCLUIA_FALLBACK_SIM=0
INCLUIA_WCPP_BIN=/home/pi/whisper.cpp/build/bin/whisper-stream
INCLUIA_WCPP_MODEL=/home/pi/whisper.cpp/models/ggml-base.bin
INCLUIA_WCPP_THREADS=4
INCLUIA_WCPP_STEP_MS=2000
INCLUIA_WCPP_LENGTH_MS=8000
INCLUIA_WCPP_VAD_THRESHOLD=0.6
```

En Windows, las rutas se guardan con `/` para evitar problemas de escape:

```env
INCLUIA_WCPP_BIN=C:/Users/Patri/Desktop/Programacion/PPS/Inclu-IA/whisper.cpp/build/bin/Release/whisper-stream.exe
INCLUIA_WCPP_MODEL=C:/Users/Patri/Desktop/Programacion/PPS/Inclu-IA/whisper.cpp/models/ggml-base.bin
```

## 4) Diagnostico

Diagnostico rapido:

```bash
cd software
python tools/check_stt_setup.py
```

Diagnostico estricto de `faster_whisper`:

```bash
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json
```

Diagnostico estricto de `whisper_cpp`:

```bash
INCLUIA_DRIVER=whisper_cpp INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json
```

Validar carga de modelo `faster_whisper`:

```bash
INCLUIA_DRIVER=faster_whisper INCLUIA_FALLBACK_SIM=0 python tools/check_stt_setup.py --json --load-model
```

## 5) API HTTP de configuracion

Leer configuracion runtime:

```bash
curl http://127.0.0.1:5000/api/config
```

Cambiar a `faster_whisper`:

```bash
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"driver":"faster_whisper","fallback_to_simulator":false,"faster_model_size":"base","faster_phrase_time_limit_s":3}'
```

Cambiar a `whisper_cpp`:

```bash
curl -X POST http://127.0.0.1:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"driver":"whisper_cpp","fallback_to_simulator":false,"whisper_cpp_step_ms":2000,"whisper_cpp_length_ms":8000}'
```

Al aplicar cambios, el backend:

1. marca el transcriber actual para detenerse;
2. actualiza `cfg` en memoria;
3. limpia `last_error`;
4. reinicia el transcriber en background;
5. emite eventos Socket.IO `config` y `status`.

## 6) Flujo recomendado de pruebas

1. Instalar ambos backends con el script del sistema operativo.
2. Correr `check_stt_setup.py --json` para `faster_whisper`.
3. Correr `check_stt_setup.py --json` para `whisper_cpp`.
4. Levantar `python server.py --driver simulator` y validar UI/red.
5. Desde el menu `⚙️`, cambiar a `faster_whisper` y hablar por microfono.
6. Desde el menu `⚙️`, cambiar a `whisper_cpp` y hablar por microfono.
7. Comparar latencia, estabilidad y calidad.
8. Copiar la configuracion elegida a `.env`.

## 7) Criterio de decision

- Usar `simulator` para pruebas de frontend, PWA, red y multiples dispositivos.
- Usar `faster_whisper` si se prioriza instalacion simple y buena calidad.
- Usar `whisper_cpp` si se prioriza tuning edge y menor dependencia Python.
- No evaluar latencia de STT mezclada con problemas de red: primero validar por archivo/diagnostico, despues microfono.
