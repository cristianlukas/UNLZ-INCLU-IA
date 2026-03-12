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
- Probar primero con microfono USB antes de Bluetooth.

## whisper.cpp falla por binario/modelo

- Verificar rutas:
  - `INCLUIA_WCPP_BIN`
  - `INCLUIA_WCPP_MODEL`
- Ejecutar `scripts/download_models.sh`.

## Latencia alta

- Reducir modelo (`tiny` o `base`).
- En `faster_whisper`, bajar `INCLUIA_FW_PHRASE_LIMIT_S`.
- En `whisper_cpp`, ajustar `INCLUIA_WCPP_STEP_MS` y `INCLUIA_WCPP_LENGTH_MS`.
- Validar VAD activo (`INCLUIA_FW_VAD=1` o `-vth` en whisper.cpp).

## Seguridad WiFi

- No usar TKIP.
- Cambiar password por una fuerte antes de demo publica.