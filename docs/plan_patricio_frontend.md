# Plan individual - Patricio (Frontend / UX / Accesibilidad)

## Mision

Entregar una interfaz web de subtitulos en vivo clara, accesible y robusta para uso real en aula.

## Alcance

Incluye:

- `web/templates/index.html`
- `web/static/app.js`
- `web/static/styles.css`
- usabilidad mobile-first
- reconexion y feedback visual de estado

No incluye:

- configuracion de AP, STT real y tuning de Raspberry Pi (eso es de Eluney)

## Entregables

1. UI de subtitulado en vivo legible a distancia.
2. Historial estable con scroll y reconexion transparente.
3. Controles de accesibilidad: tamano de fuente, contraste, limpieza.
4. Onboarding de conexion (SSID + URL local) claro.
5. Modo demo/replay usable sin backend real.

## Plan semanal

1. Semana 1
- consolidar layout mobile-first
- validar `status`, `caption`, `history` con `simulator`
- pruebas en pantallas pequenas y medianas

2. Semana 2
- mejorar legibilidad real (tipografia, espaciado, jerarquia)
- pulir estados no tecnicos para usuarios finales
- test con 3 clientes simultaneos

3. Semana 3
- cerrar modo demo/replay
- mejorar onboarding y feedback de red local
- validar funcionamiento offline (sin CDN)

4. Semana 4
- ajuste final de UX en prueba integrada
- checklist final de accesibilidad para demo

## Dependencias y anti-bloqueo

- No depende de STT real para avanzar.
- Trabaja con `INCLUIA_DRIVER=simulator` y contrato de eventos fijo.
- Puede iterar UX aunque backend este ajustando modelos.

## Definition of done (individual)

- UI estable 30 min sin recarga manual.
- Subtitulos legibles en Android/iOS.
- Reconexion automatica funcionando.
- PRs mergeados con mejoras de UX y documentacion de pruebas.
