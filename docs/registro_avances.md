# Registro de Avances de Becarios

Este documento sirve como bitácora centralizada para que Patricio (Frontend) y Eluney (Backend) registren su progreso, decisiones técnicas y bloqueos de manera periódica.

## Sugerencias de uso
- Escribir entradas breves al finalizar la semana (o jornadas importantes).
- Incluir enlaces a PRs (Pull Requests) o commits relevantes.
- Mencionar si hubo alguna duda sobre el contrato de eventos o decisiones de diseño.

---

## Eluney (Backend / STT / Raspberry Pi)

### Semana 1
- **Fecha:** 15/04/2026
- **Avances:** 
  - Esta semana logre instalar todo lo necesario en la raspberry pi 4.
  - Realice el [benchmark de algunos modelos STT](https://github.com/cristianlukas/UNLZ-INCLU-IA/commit/e26be5b7767bd9594cc0fa6bc109846883d38f31), siendo faster_whisper tiny y vosk los más prometedores para subtitulado en tiempo real.
- **Problemas/Bloqueos:**
  - Detecte que desde telefonos los subtitulos se congelaban, pero desde PC se mostraban correctamente.
  - 

### Semana 2
- **Fecha:** 08/06/2026
- **Avances:** 
  - Realice la prueba larga de 20 minutos utilizando el perfil 1.
  - Microfono Inalambrico F11-2 con conexion usb al adaptador UGREEN USB 3.0 Macho a USB-C Hembra.
  - La duracion de la prueba fue de 20 minutos.
  - El audio se saturo aproximadamente unas 64 veces, cabe destacar que al llegar a los 19 minutos de prueba estuvo saturado durante 1 minuto aproximadamente.
  - La percepcion de la latencia es baja al comienzo, aproximadamente 10 segundos, que luego suben a 21 segundos y combinados con los eventos de saturacion llevan a una calidad no tan deseable.
  - La decision es volver a realizar las pruebas con el perfil 2, si el mismo falla podriamos intentar mejorar un poco el hardware, el procesamiento de la pi4 se mantiene entre el 80% y 90%, pero la velocidad de generacion de subtitulos es suboptima.
- **Problemas/Bloqueos:**
  - Tuve inconvenientes al realizar una prueba manual del servidor con driver faster_whisper, lo reporte como issue y fue solucionado.
---

## Patricio (Frontend / UX / Accesibilidad)

### Semana 1
- **Fecha:** 15/03/2026
- **Avances:** 
  - Cambios a nivel UI, accesibilidad y ajustes en el theme (6e45f7536efa3de85a37c03d7d5be359d9d85f6c)
- **Problemas/Bloqueos:**
  - Sin bloqueos

### Semana 2
- **Fecha:** 19/03/2026
- **Avances:**
  - Modificación para habilitar la app en modo PWA, además hice pruebas de carga, conectando multiples dispositivos (310efe287b506e0ad6c4ecfb8a8ebb3a3650bf82)
- **Problemas/Bloqueos:**
  - No logré que funcione la PWA desde fuera de localhost, hay un problema de certificados donde para ser PWA se requiere que la app se sirva a través de https, y no logré cargar correctamente el certificado

### Semana 3

* **Fecha:** 21/05/2026
* **Avances:**

  * Se realizaron pruebas funcionales de los modos Demo y Replay en múltiples dispositivos Android y equipos Windows.
  * Se validó el funcionamiento del historial, cambio entre modos y comportamiento general de la interfaz.
  * Se realizaron pruebas de estabilidad manteniendo la aplicación abierta durante períodos prolongados sin detectar bloqueos ni necesidad de recarga manual.
  * Se verificó el correcto funcionamiento de la PWA y del service worker en los dispositivos utilizados.
* **Problemas/Bloqueos:**

  * No fue posible realizar una validación completa del modo En vivo debido a problemas de rendimiento y fluidez en la instancia local de Whisper utilizada para las pruebas, sospecho que puede ser porque no esta optimizado para windows o quizas mi notebook esta un poco lenta, lo voy a validar con backend.
  * Queda pendiente la validación en dispositivos iOS para la semana4.


### Semana 4
- **Fecha:** DD/MM/AAAA
- **Avances:** 
- **Problemas/Bloqueos:**
