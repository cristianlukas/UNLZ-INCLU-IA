# Plan de implementacion: traduccion en tiempo real

## 1. Objetivo

Agregar un modo de operacion que capture habla en ingles, la transcriba localmente y publique subtitulos traducidos al espanol desde la Raspberry Pi, sin internet ni APIs externas.

El modo actual de subtitulado en espanol debe seguir funcionando sin cambios para los usuarios que no activen la traduccion.

## 2. Alcance del MVP

### Incluido

- Audio en ingles desde el mismo microfono utilizado por Inclu-IA.
- Reconocimiento de voz local con Whisper/`whisper.cpp`, configurado con idioma `en`.
- Traduccion local ingles -> espanol mediante un motor/modelo dedicado.
- Publicacion de la traduccion por el evento existente `caption`.
- Selector de modo desde la configuracion runtime y por variables de entorno.
- Funcionamiento offline despues de instalar y descargar los modelos.
- Metricas de latencia, errores y uso de memoria en Raspberry Pi.

### Fuera del MVP

- Traduccion inversa espanol -> ingles.
- Deteccion automatica de idioma.
- Traduccion mediante un LLM generalista.
- Correccion editorial avanzada o resumen del discurso.
- Traduccion de varios idiomas simultaneamente.

## 3. Arquitectura propuesta

```text
Microfono
   -> captura/VAD/chunking
   -> STT local (Whisper, idioma en)
   -> texto original en ingles
   -> traductor local (ingles -> espanol)
   -> evento Socket.IO caption
   -> clientes web
```

Whisper no debe recibir `language=es` en este modo: el audio es ingles y debe configurarse explicitamente como `en`. La opcion `translate` de Whisper no resuelve este caso porque traduce a ingles; para ingles -> espanol se necesita una segunda etapa.

El traductor debe cargarse una sola vez y permanecer residente, igual que el modelo STT. La interfaz puede continuar mostrando el campo `text` como hasta ahora, usando allí la traduccion.

## 4. Diseño de configuracion

Agregar a `AppConfig`:

```env
INCLUIA_MODE=transcribe
INCLUIA_SOURCE_LANGUAGE=es
INCLUIA_TARGET_LANGUAGE=es
INCLUIA_TRANSLATOR=argos
INCLUIA_TRANSLATOR_MODEL_DIR=./models/translation
```

Valores iniciales:

- `transcribe`: conserva el comportamiento actual.
- `translate`: usa `en` como idioma de origen y `es` como destino.
- `INCLUIA_TRANSLATOR`: debe permitir cambiar el backend sin modificar el pipeline STT.

La API `/api/config` debe exponer el modo y los idiomas. El `POST /api/config` debe validar que el modo y el traductor sean valores permitidos y reiniciar ordenadamente el pipeline, como ya hace al cambiar de driver.

## 5. Cambios de software

### 5.1. Capa de traduccion

Crear una abstraccion `Translator`, independiente de los drivers STT, con una interfaz equivalente a:

```python
translate(text: str) -> str
```

Implementar primero un adaptador local para el motor elegido. El adaptador debe:

- cargar el modelo durante la inicializacion;
- rechazar textos vacios;
- devolver errores claros si falta el modelo;
- ser seguro para una sola llamada concurrente durante el MVP;
- permitir reemplazo futuro por otro motor.

La eleccion entre Argos Translate y un modelo OPUS-MT/Marian debe cerrarse después de una prueba en la Raspberry Pi. El criterio principal es latencia sostenida y calidad, no el benchmark de otra computadora.

### 5.2. Pipeline STT

Agregar un wrapper de pipeline que:

1. ejecute el transcriptor con idioma `en` cuando el modo sea `translate`;
2. conserve el texto original del segmento;
3. traduzca solo segmentos finales o suficientemente estables;
4. emita la traduccion al cliente;
5. informe estado y errores sin detener el servidor completo.

No se deben traducir repetidamente todos los parciales del mismo segmento: eso aumenta el costo y puede producir texto duplicado o inestable.

### 5.3. Contrato de eventos

Mantener compatibilidad con clientes actuales:

```json
{
  "id": "...",
  "text": "Hola, ¿cómo están?",
  "is_final": true,
  "source": "whisper_cpp",
  "mode": "translate",
  "source_language": "en",
  "target_language": "es",
  "original_text": "Hello, how are you?"
}
```

Los campos nuevos deben ser opcionales para que clientes antiguos sigan funcionando. En modo `transcribe`, `text` continúa siendo la transcripcion y `original_text` puede omitirse.

### 5.4. Interfaz web

Agregar en el panel de configuracion:

- modo: `Subtitular` / `Traducir ingles a espanol`;
- idioma de origen visible;
- idioma de destino visible;
- estado del traductor y errores de carga.

El modo activo debe aparecer también junto a la fuente para que el usuario sepa si está viendo una transcripción o una traducción.

## 6. Plan de ejecución por fases

### Fase 0: línea base

- Ejecutar los benchmarks actuales de `whisper_cpp` y `faster_whisper`.
- Registrar modelo, temperatura, RAM, latencia y factor de tiempo real.
- Preparar audios repetibles en inglés y sus traducciones esperadas.

### Fase 1: selección del traductor

- Probar al menos dos alternativas locales compatibles con Linux ARM64.
- Medir carga inicial, RAM adicional, latencia por frase y calidad.
- Verificar que el modelo pueda descargarse previamente y ejecutarse sin red.
- Elegir una alternativa para el MVP y documentar la decisión.

### Fase 2: backend

- Incorporar `Translator` y su adaptador.
- Incorporar modo e idiomas a `AppConfig` y `.env`.
- Integrar traduccion después de segmentos finales.
- Agregar logs y estados `loading`, `translating`, `ready` y `error`.
- Mantener fallback explícito: un fallo del traductor no debe presentar una traducción inventada; debe informar error y conservar el modo anterior o detener el modo traducción según la configuración.

### Fase 3: contrato y frontend

- Documentar los nuevos campos del evento `caption`.
- Agregar controles de modo en la webapp.
- Mostrar claramente texto traducido y, opcionalmente, texto original.
- Probar reconexión, historial y múltiples celulares.

### Fase 4: validación en Raspberry Pi

- Probar con frases cortas, habla continua, pausas y ruido de aula.
- Verificar que la traducción no se acumule ni duplique segmentos.
- Medir latencia desde el final de la frase hasta el subtítulo traducido.
- Ejecutar una prueba sostenida de al menos 15 minutos.
- Registrar temperatura, throttling, RAM y cantidad de errores.

### Fase 5: documentación y despliegue

- Actualizar instalación, configuración, uso y troubleshooting.
- Incluir descarga/versionado de modelos de traducción.
- Agregar un chequeo a `check_stt_setup.py` o crear un chequeo equivalente para traducción.
- Actualizar el servicio systemd y el instalador solo si el modelo requiere dependencias adicionales.

## 7. Criterios de aceptación

- El modo actual español -> español sigue funcionando.
- En modo traducción, una frase inglesa produce texto español entendible sin internet.
- El servidor no descarga modelos ni consulta servicios externos durante la operación.
- El primer modelo se carga antes de atender al usuario o se informa claramente su estado.
- No se emiten traducciones vacías, duplicadas o basadas en parciales obsoletos.
- La API y la webapp permiten cambiar de modo sin reiniciar manualmente el servicio.
- El flujo funciona con al menos tres celulares conectados al AP local.
- La latencia y el uso de recursos quedan medidos en la Raspberry objetivo.
- Existen pruebas automatizadas para configuración, contrato de eventos y adaptador del traductor.

## 8. Riesgos y decisiones pendientes

| Riesgo | Mitigación |
|---|---|
| Traducción demasiado lenta en Pi 4 | Traducir solo finales, usar modelo compacto y medir antes de integrar por defecto |
| Frases cortadas por ventanas STT | Usar VAD, pausa breve y consolidación de segmentos |
| Traducciones repetidas | Identificar segmentos por ID y traducir solo cambios finales |
| Modelo incompatible con ARM64 | Validar instalación en la Pi antes de cerrar la dependencia |
| Falta de RAM | Mantener modelos residentes y medir el consumo conjunto |
| Cliente antiguo incompatible | Hacer opcionales todos los campos nuevos del evento |
| Error del traductor | Exponer estado/error y evitar mostrar resultados inventados |

Decisiones que deben tomarse durante la Fase 1:

1. Motor y modelo de traducción definitivos.
2. Latencia máxima aceptable para el aula.
3. Si se muestra también el texto original en la interfaz.
4. Si el modo traducción será seleccionado manualmente o quedará fijado por configuración.

## 9. Resultado esperado

El resultado final será un único appliance local con dos usos seleccionables:

- subtitulado de español en tiempo real;
- traducción de habla inglesa a subtítulos en español.

Ambos compartirán captura, red local, historial, reconexión y contrato base de eventos, manteniendo separadas las responsabilidades de reconocimiento y traducción.
