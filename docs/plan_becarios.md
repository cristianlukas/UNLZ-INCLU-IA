# Plan de trabajo para becarios (paralelo y no bloqueante)

Este documento es la referencia principal para coordinar a Patricio (frontend) y Eluney (backend) sin dependencias bloqueantes.

Planes individuales detallados:

- `docs/plan_eluney_backend.md`
- `docs/plan_patricio_frontend.md`
- `docs/registro_avances.md` (Para asentar progreso y bloqueos semanales)

## 1) Objetivo final

Construir y demostrar un sistema de subtitulado en tiempo real para aula con estas condiciones de cierre:

- Raspberry Pi funcionando como AP WiFi local (`wlan0`, sin internet).
- Captura de audio desde microfono inalambrico (USB o Bluetooth).
- Transcripcion en la Raspberry (CPU) con Whisper.
- Broadcast de subtitulos a multiples celulares conectados al AP.
- Web accesible, legible en tiempo real y estable durante clase.

Criterio de exito final (demo):

- 1 Raspberry Pi + al menos 5 celulares conectados + subtitulos en vivo por 30 minutos sin caida del servicio.

## 2) Lo que esta hecho hasta ahora

Estado actual del repo (implementado):

- Backend Flask + Flask-SocketIO funcional.
- Contrato de eventos estable (`status`, `caption`, `history`, `history_cleared`).
- Historial de captions y endpoint de salud (`/_health`).
- Drivers desacoplados de transcripcion:
  - `simulator` (desarrollo y pruebas desacopladas)
  - `faster_whisper`
  - `whisper_cpp`
- Fallback automatico a simulador si un driver real falla.
- Frontend mobile-first funcional:
  - subtitulo en vivo
  - historial
  - reconexion
  - alto contraste
  - tamano de fuente
- Configuracion de red AP lista:
  - `software/config/hostapd.conf`
  - `software/config/dnsmasq.conf`
- Scripts operativos:
  - `scripts/setup_ap_networkmanager.sh`
  - `scripts/setup_ap_hostapd_dnsmasq.sh`
  - `scripts/install_backend.sh`
  - `scripts/download_models.sh`
- Servicio `systemd`:
  - `deploy/inclu-ia.service`
- Documentacion base:
  - instalacion, uso, troubleshooting y contrato de eventos.

## 3) Tareas divididas y plan por becario (trabajo en paralelo)

### Reglas de desacople (obligatorias)

- El contrato de eventos definido en `docs/contrato_eventos.md` se considera congelado (v1) para esta etapa.
- Patricio no depende de STT real: trabaja contra `INCLUIA_DRIVER=simulator`.
- Eluney no depende del frontend para validar backend: usa `/_health`, logs y clientes Socket.IO de prueba.
- Cambios de contrato solo en checkpoints acordados (no durante la semana sin aviso).
- Cada becario trabaja en su rama y abre PR pequeno, frecuente y revisable.

### Plan de Eluney (Backend / Pi / STT)

Objetivo individual:

- Entregar backend estable en Raspberry Pi con STT real y operacion continua.

Referencia detallada:

- `docs/plan_eluney_backend.md`

Entregables:

1. Pipeline `faster_whisper` estable en Pi con VAD y latencia aceptable.
2. Pipeline `whisper_cpp` funcionando como alternativa medible.
3. Seleccion de driver por defecto basada en metricas reales (latencia y estabilidad).
4. Servicio `systemd` operando en autostart con logs claros.
5. Guia de configuracion de microfono (USB y Bluetooth) validada en campo.

Plan por semanas (sin bloquear frontend):

1. Semana 1:
- levantar backend en Pi con `simulator`
- validar AP + Socket.IO + health endpoints
- instrumentar logs minimos de estado/errores

2. Semana 2:
- habilitar `faster_whisper`
- ajustar chunking (`INCLUIA_FW_PHRASE_LIMIT_S`) y VAD
- correr prueba de 20 min y registrar latencia percibida

3. Semana 3:
- habilitar `whisper_cpp`
- comparar CPU/RAM/latencia contra `faster_whisper`
- documentar decision de driver por defecto

4. Semana 4:
- hardening final (autostart, reconexion, recuperacion de errores)
- prueba larga de 30-40 min con clientes reales

Definition of done individual (Eluney):

- El servicio arranca al boot.
- `/_health` responde estable durante toda la prueba.
- STT real operativo en al menos 1 microfono validado.
- Driver por defecto decidido y documentado.

### Plan de Patricio (Frontend / UX / Accesibilidad)

Objetivo individual:

- Entregar una UI web clara, legible y robusta para estudiantes en aula.

Referencia detallada:

- `docs/plan_patricio_frontend.md`

Entregables:

1. Pantalla principal de subtitulos en vivo con lectura a distancia.
2. Historial util y estable con reconexion transparente.
3. Controles de accesibilidad (tamano de letra, contraste, limpieza de historial).
4. Onboarding claro de conexion (SSID + URL local).
5. Modo demo/replay para pruebas sin backend real.

Plan por semanas (sin bloquear backend):

1. Semana 1:
- cerrar layout mobile-first con `simulator`
- validar estados de conexion y reconexion
- pruebas en 2-3 tamanos de pantalla

2. Semana 2:
- mejorar legibilidad real de captions (espaciado, scroll, jerarquia visual)
- ajustar mensajes de estado para usuario no tecnico
- test manual con 3 clientes simultaneos

3. Semana 3:
- terminar modo demo/replay
- optimizar onboarding y feedback de red
- pulir comportamiento offline (sin CDN)

4. Semana 4:
- ajuste final de UX en prueba de aula real
- documentar checklist de validacion visual

Definition of done individual (Patricio):

- UI usable en Android/iOS sin instalar app.
- Subtitulos legibles y estables durante 30 min.
- Reconexion sin recargar manualmente.
- Onboarding entendible en menos de 1 minuto.

### Checkpoints de integracion (minimos, para no bloquear)

Solo 3 checkpoints obligatorios:

1. Fin semana 1: confirmar que contrato de eventos no cambia.
2. Fin semana 2: validar UI con STT real (solo ajuste de contenido, no estructura de eventos).
3. Fin semana 4: ensayo general de demo.

Fuera de esos puntos, cada uno avanza por su carril.

### Matriz de dependencias (anti-bloqueo)

- Patricio depende de Eluney: no (usa simulador y contrato fijo).
- Eluney depende de Patricio: no (valida via API/logs/socket test).
- Integracion final: si, en checkpoints definidos.

### Criterios de aceptacion global

El proyecto se considera listo para entrega cuando se cumple todo:

- Red AP local funcionando y accesible por celulares.
- Backend STT estable en Raspberry Pi.
- Frontend accesible y legible en uso real de aula.
- Prueba integrada de 30 min superada con multiples clientes.
- Documentacion de instalacion/uso suficiente para replicar la demo desde cero.
