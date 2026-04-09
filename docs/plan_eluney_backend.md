# Plan individual - Eluney (Backend / Raspberry Pi / STT)

Documento principal de ejecucion:

- `docs/guia_eluney_luna_tests_stt.md`

Este plan corresponde a **Eluney Luna**.
No confundir con `docs/plan_patricio_frontend.md`, que corresponde a Patricio Garces.

## Mision

Dejar el backend de Inclu-IA estable en Raspberry Pi, con transcripcion real y operacion continua para clase.

## Alcance

Incluye:

- servicio backend (`software/server.py`, `software/incluia/*`)
- drivers STT (`faster_whisper`, `whisper_cpp`)
- red AP en Pi
- service `systemd`
- validaciones de latencia/estabilidad

No incluye:

- cambios de UX/CSS del frontend (eso es de Patricio)

## Entregables

1. Backend operativo en Pi con `INCLUIA_DRIVER=faster_whisper`.
2. Backend operativo en Pi con `INCLUIA_DRIVER=whisper_cpp`.
3. Documento comparativo simple (latencia, CPU, estabilidad) y driver recomendado.
4. Servicio `systemd` arrancando al boot sin intervencion manual.
5. Checklist de audio real (USB y/o Bluetooth) validado.

## Plan semanal

1. Semana 1
- levantar AP + backend en `simulator`
- validar `/api/config`, `/api/history`, `/_health`
- confirmar logs de estado y errores

2. Semana 2
- habilitar `faster_whisper`
- ajustar `INCLUIA_FW_PHRASE_LIMIT_S`, `INCLUIA_FW_VAD`
- prueba de 20 min con registro de incidencias

3. Semana 3
- habilitar `whisper_cpp`
- tuning de `INCLUIA_WCPP_STEP_MS`, `INCLUIA_WCPP_LENGTH_MS`
- comparativa con evidencia de prueba

4. Semana 4
- hardening final + autostart
- prueba integrada de 30-40 min

## Dependencias y anti-bloqueo

- No depende de frontend para avanzar.
- Usa contrato fijo de `docs/contrato_eventos.md`.
- Si UI cambia, backend no se frena mientras respete contrato.

## Definition of done (individual)

- Servicio estable en Pi durante 30 min.
- Al menos un microfono real validado.
- Driver por defecto decidido y documentado.
- PRs mergeados con cambios reproducibles en docs.
