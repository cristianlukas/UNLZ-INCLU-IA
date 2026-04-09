# Troubleshooting

## El servidor no arranca

- Revisar dependencias:

```bash
cd /home/pi/Inclu-IA/software
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
- Si falla driver real y `INCLUIA_FALLBACK_SIM=1`, debe entrar a simulador.
- Si no queres fallback, poner `INCLUIA_FALLBACK_SIM=0` para diagnostico estricto.

## faster-whisper no captura audio

- Revisar que el microfono este visible para ALSA/PyAudio.
- Definir `INCLUIA_AUDIO_DEVICE_INDEX` con un indice valido.
- Si el adaptador USB trabaja a otra frecuencia, definir `INCLUIA_AUDIO_SAMPLE_RATE` (por ejemplo `48000`).
- Probar primero con microfono USB antes de Bluetooth.

## whisper.cpp falla por binario/modelo

- Verificar rutas:
  - `INCLUIA_WCPP_BIN`
  - `INCLUIA_WCPP_MODEL`
- Ejecutar `scripts/download_models.sh`.

## Latencia alta

- Reducir modelo (`tiny` o `base`).
- En Raspberry Pi 4, `small` suele mejorar precision pero aumentar mucho la demora; no asumir tiempo real.
- En `faster_whisper`, bajar `INCLUIA_FW_PHRASE_LIMIT_S`.
- En `whisper_cpp`, ajustar `INCLUIA_WCPP_STEP_MS` y `INCLUIA_WCPP_LENGTH_MS`.
- Validar VAD activo (`INCLUIA_FW_VAD=1` o `-vth` en whisper.cpp).

## Seguridad WiFi

- No usar TKIP.
- Cambiar password por una fuerte antes de demo publica.
## Console muestra GET /socket.io/socket.io.js 400

- Causa tipica: cliente JS de Socket.IO no compatible o path legado.
- En este repo el cliente correcto es local: /static/vendor/socket.io.min.js.
- Si el navegador mantiene cache viejo, forzar recarga con Ctrl+F5.

