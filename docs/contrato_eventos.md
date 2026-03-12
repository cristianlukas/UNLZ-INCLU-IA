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

## Eventos client -> server

### `clear_history`

Sin payload. Solicita limpieza de historial global.

## Endpoints HTTP asociados

- `GET /api/config`
- `GET /api/history`
- `POST /api/clear`
- `GET /_health`