# Contrato de eventos Socket.IO

Este contrato define la interfaz backend <-> frontend para Inclu-IA.

## Eventos server -> client

### `status`

Payload:

```json
{
  "state": "idle|listening|transcribing|error",
  "detail": "string",
  "t_server_ms": 1741710000000
}
```

Semantica:

- `idle`: inicializando o sin captura activa.
- `listening`: esperando voz.
- `transcribing`: procesando audio.
- `error`: fallo recuperable/no recuperable.

### `caption`

Payload:

```json
{
  "id": "uuid",
  "text": "texto transcripto",
  "t0_ms": 120,
  "t1_ms": 2150,
  "is_final": true,
  "t_server_ms": 1741710001234,
  "source": "simulator|faster_whisper|whisper_cpp"
}
```

Reglas:

- `is_final=false`: caption parcial en progreso.
- `is_final=true`: caption consolidada para historial.

### `history`

Payload:

```json
{
  "items": [
    {
      "id": "uuid",
      "text": "caption final",
      "is_final": true,
      "t_server_ms": 1741710001234,
      "source": "faster_whisper"
    }
  ]
}
```

Uso: sincronizar clientes que se conectan tarde.

### `history_cleared`

Payload:

```json
{
  "t_server_ms": 1741710011000
}
```

Uso: vaciar historial en todos los clientes.

### `config`

Payload:

```json
{
  "driver": "faster_whisper",
  "active_source": "faster_whisper",
  "ap_ssid": "Inclu-IA_Classroom",
  "ap_url": "http://192.168.4.1:5000",
  "history_size": 200,
  "socket_transport": "polling",
  "fallback_to_simulator": false,
  "last_error": null,
  "status": {
    "state": "idle",
    "detail": "Reiniciando driver faster_whisper",
    "t_server_ms": 1741710000000
  },
  "stt": {
    "driver": "faster_whisper",
    "driver_options": ["faster_whisper", "simulator", "whisper_cpp"],
    "faster_model_size": "base",
    "faster_compute_type": "int8",
    "faster_language": "es",
    "faster_phrase_time_limit_s": 3,
    "faster_vad_filter": true,
    "faster_queue_max_chunks": 6,
    "whisper_cpp_threads": 4,
    "whisper_cpp_step_ms": 2000,
    "whisper_cpp_length_ms": 8000,
    "whisper_cpp_vad_threshold": 0.6
  }
}
```

Uso: sincronizar clientes cuando se aplica una configuracion STT runtime desde la webapp o API.

## Eventos client -> server

### `clear_history`

Sin payload. Solicita limpieza de historial global.

## Endpoints HTTP asociados

- `GET /api/config`
- `POST /api/config`
- `GET /api/history`
- `POST /api/clear`
- `GET /_health`

### `GET /api/config`

Devuelve la configuracion runtime actual, incluyendo driver activo, estado, fallback y parametros STT.

### `POST /api/config`

Aplica cambios runtime al STT y reinicia el transcriber.

Payload aceptado:

```json
{
  "driver": "simulator|faster_whisper|whisper_cpp",
  "fallback_to_simulator": false,
  "faster_model_size": "tiny|base|small",
  "faster_phrase_time_limit_s": 3,
  "faster_queue_max_chunks": 6,
  "faster_vad_filter": true,
  "whisper_cpp_threads": 4,
  "whisper_cpp_step_ms": 2000,
  "whisper_cpp_length_ms": 8000,
  "whisper_cpp_vad_threshold": 0.6
}
```

Respuesta exitosa:

```json
{
  "ok": true,
  "config": {
    "driver": "faster_whisper",
    "active_source": "faster_whisper",
    "stt": {
      "driver": "faster_whisper"
    }
  }
}
```

Respuesta invalida:

```json
{
  "ok": false,
  "error": "Driver invalido: bad_driver. Usa simulator, faster_whisper o whisper_cpp."
}
```

Nota: este endpoint no persiste cambios en `software/.env`; solo modifica el proceso actual.
