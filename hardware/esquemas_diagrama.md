# Esquema funcional de hardware

## Componentes minimos

- Raspberry Pi 4 (4 GB o mas) o Raspberry Pi 5.
- Microfono inalambrico (ideal USB dongle, Bluetooth como opcion).
- Fuente de alimentacion estable.
- (Opcional) carcasa + ventilacion para uso continuo.

## Flujo fisico

1. Docente habla al microfono.
2. Raspberry captura audio local.
3. Motor STT transcribe en CPU.
4. Raspberry publica subtitulos por WiFi AP local.
5. Estudiantes abren la web de subtitulos desde celular.

## Topologia de red

- Interfaz AP: `wlan0`
- IP AP sugerida: `192.168.4.1/24`
- SSID sugerido: `Inclu-IA_Classroom`
- URL sugerida: `http://192.168.4.1:5000`