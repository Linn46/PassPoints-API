# Capturas para el capítulo 3

Las imágenes de `capturas/` se obtuvieron navegando la interfaz local de
PassPoints. Las secciones y pies siguientes son sugerencias; ajusta la
numeración a la estructura final de la tesis.

| Archivo | Sección sugerida | Pie de figura sugerido |
|---|---|---|
| `captura_02_seleccion.png` | 3.1 Entorno de ejecución | **Figura 3.1.** Prototipo de PassPoints durante el registro, con cinco puntos seleccionados sobre el fondo «Forest trail» y sin datos personales. |
| `captura_01_acceso.png` | 3.2 Pantalla de acceso | **Figura 3.2.** Pantalla inicial de PassPoints con las opciones de registro e inicio de sesión y los campos vacíos. |
| `captura_03_respuesta_analisis.png` | 3.3 Respuesta al análisis | **Figura 3.3.** Resultado visible del análisis de una selección de ejemplo sin patrones débiles detectados. |
| `captura_03b_analisis_completo.png` | 3.3 Respuesta al análisis | Captura de página completa que conserva el contexto de la interfaz y la respuesta anterior. |
| `captura_04_validacion_puntos.png` | 3.4 Validación de selección | **Figura 3.4.** Mensaje de validación cuando se intenta colocar dos puntos demasiado próximos durante el registro. |
| `captura_05_respuesta_patron_debil.png` | 3.5 Detección de patrones débiles | **Figura 3.5.** La interfaz muestra la advertencia de puntos agrupados devuelta por el análisis. |
| `captura_06_explicacion_patron.png` | 3.5.1 Explicación al usuario | **Figura 3.6.** Diálogo con la explicación y recomendación asociadas al patrón agrupado. |
| `captura_07_login.png` | 3.6 Inicio de sesión | **Figura 3.7.** Formulario de inicio de sesión con imagen seleccionada y una secuencia de cinco puntos. |
| `captura_08_rechazo_acceso.png` | 3.6.1 Rechazo de credenciales | **Figura 3.8.** Mensaje mostrado después de un intento de acceso con credenciales no registradas; la API respondió HTTP 401. |
| `error_puntos_duplicados.png` | 3.4.1 Validación de solicitudes de análisis | **Figura 3.9.** Respuesta HTTP 422 de `POST /api/v1/analysis` al enviar cinco puntos con dos coordenadas duplicadas. |
| `error_colinealidad.png` | 3.4.1 Validación de solicitudes de análisis | **Figura 3.10.** Respuesta HTTP 400 de `POST /api/v1/analysis` al enviar cinco puntos distintos colineales; el cuerpo identifica el tipo `collinear_points`. |
| `swagger_api.png` | 3.2 Documentación de la API | **Figura 3.11.** Vista general de Swagger UI con las operaciones de análisis, salud y autenticación, y los esquemas disponibles. |
| `figura_3_12_pytest.png` | 3.12 Verificación mediante pruebas automatizadas | **Figura 3.12.** Ejecución completa de Pytest: 150 aprobadas, 0 omitidas, 0 fallidas y 4 advertencias. |
| `entorno_usabilidad_propuesto.png` | 3.13 Procedimiento de ejecución (diseño del estudio) | **Figura 3.13.** Entorno digital propuesto para las tareas de registro y autenticación; el prototipo aparece en estado inicial, sin participantes ni datos personales. No representa una sesión de usabilidad ejecutada. |

## Alcance de las capturas

- Los análisis y las secuencias son demostraciones controladas para documentar
  el comportamiento del sistema; no son resultados de una prueba con
  participantes.
- El intento de inicio de sesión usó la dirección reservada
  `cap3-demo@example.test`, que no identifica a una persona. Solo se hizo una
  consulta de acceso; no se creó ni modificó una cuenta.
- La validación de puntos próximos se genera en la interfaz antes de enviar
  una petición al backend.
- La captura de error 401 muestra la respuesta real del backend y el mensaje
  correspondiente de la interfaz.
- Las capturas de puntos duplicados y colinealidad muestran respuestas reales
  del backend obtenidas desde Swagger UI. Se enviaron datos de prueba
  controlados, no datos de usuarios ni de participantes. La interfaz de
  selección puede impedir algunos casos localmente; por eso estas dos figuras
  documentan directamente la validación del endpoint de análisis.
- La Figura 3.13 documenta únicamente el prototipo en estado inicial como
  entorno digital previsto. No hubo participantes en esa captura ni debe
  presentarse como evidencia de una sesión realizada.

## Ejecución de pruebas

La suite se ejecuta desde la raíz del proyecto con:

    .venv/bin/pytest -q --tb=short

Resultado de la ejecución capturada: **150 passed, 0 skipped, 0 failed**,
con cuatro advertencias de deprecación de dependencias/configuración. El
resumen del capítulo debe usar estos valores actuales, no 44 aprobadas y 7
omitidas.
