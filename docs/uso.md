# Uso diario

## Inicio manual (sin systemd)

```bash
cd /home/pi/Inclu-IA/software
source .venv/bin/activate
python server.py
```

Opciones:

```bash
python server.py --driver simulator --host 0.0.0.0 --port 5000
python server.py --driver faster_whisper
python server.py --driver whisper_cpp
```

## Inicio con systemd

```bash
sudo systemctl start inclu-ia.service
sudo systemctl restart inclu-ia.service
sudo systemctl stop inclu-ia.service
sudo systemctl status inclu-ia.service
```

Logs en vivo:

```bash
journalctl -u inclu-ia.service -f
```

## Endpoints utiles

- Health: `GET /_health`
- Config: `GET /api/config`
- Historial: `GET /api/history`
- Limpieza historial: `POST /api/clear`

## Flujo recomendado de clase

1. Encender Raspberry Pi.
2. Verificar AP arriba (`nmcli c show --active` o `ip a`).
3. Verificar servicio (`systemctl status`).
4. Conectar celulares al AP.
5. Abrir URL local y validar estado `Escuchando`.

## Notas de driver

- `simulator`: para desarrollo frontend y pruebas de red.
- `faster_whisper`: pipeline Python simple para MVP.
- `whisper_cpp`: opcion para tuning de latencia en edge.