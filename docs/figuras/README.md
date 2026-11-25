# Figuras de PassPoints para el capítulo 2

Las imágenes 01–03 y 09–11 se obtuvieron de los recursos y la interfaz reales
del proyecto. Las figuras geométricas se contrastaron con las respuestas del
endpoint `POST /api/v1/analysis` y las funciones del backend.

**Nota metodológica:** las selecciones de las figuras 03–11 son ejemplos
controlados creados para explicar el método. No corresponden a participantes ni
deben presentarse como resultados de un experimento con usuarios.

## Figuras listas para insertar

| Archivo | Sección sugerida del capítulo 2 | Pie de figura sugerido |
|---|---|---|
| `figura_01_catalogo_fondos.png` | 2.1 Recursos visuales de PassPoints | **Figura 2.1.** Catálogo de los 21 fondos SVG disponibles en PassPoints-API. Fuente: `frontend/assets/images/`. |
| `figura_02_fondo.png` | 2.1.1 Fondo seleccionado | **Figura 2.2.** Fondo «Forest trail» del catálogo de imágenes incluido en PassPoints-API. Fuente: recurso `frontend/assets/images/forest-trail.svg`. |
| `figura_03_interfaz_seleccion.png` | 2.2 Selección de la contraseña gráfica | **Figura 2.3.** Interfaz de PassPoints con cinco puntos seleccionados sobre el fondo «Forest trail». La selección es ilustrativa y no corresponde a datos experimentales. |
| `figura_04_delaunay.png` | 2.3 Triangulación de Delaunay | **Figura 2.4.** Triangulación de Delaunay generada por el endpoint de análisis para la selección ilustrativa de cinco puntos. |
| `figura_05_angulos.png` | 2.3.1 Análisis angular | **Figura 2.5.** Ángulos interiores, en grados, de los triángulos de Delaunay; calculados mediante las funciones geométricas del backend. |
| `figura_06_envolvente_convexa.png` | 2.4 Envolvente convexa | **Figura 2.6.** Envolvente convexa de los cinco puntos de la selección ilustrativa. |
| `figura_07_distancias.png` | 2.5 Distancias euclidianas | **Figura 2.7.** Distancias euclidianas entre los diez pares de puntos de la selección, expresadas en píxeles. |
| `figura_08_sistema_coordenadas.png` | 2.2.1 Coordenadas de la imagen | **Figura 2.8.** Sistema de coordenadas de la imagen de 1920 × 1080 píxeles, con origen en la esquina superior izquierda y coordenadas de una selección de referencia. |
| `figura_09_distribucion_agrupada.png` | 2.6 Ejemplo de selección agrupada | **Figura 2.9.** Cinco puntos próximos sobre el fondo «Forest trail». La respuesta del análisis clasificó la selección como agrupada. |
| `figura_10_distribucion_lineal.png` | 2.6 Ejemplo de selección lineal | **Figura 2.10.** Cinco puntos aproximadamente alineados sobre el fondo «Forest trail». La respuesta del análisis clasificó la selección como patrón Line. |
| `figura_11_distribucion_regular.png` | 2.6 Ejemplo de selección regular | **Figura 2.11.** Cinco puntos distribuidos en una cuadrícula sobre el fondo «Forest trail». La respuesta del análisis clasificó la selección como regular. |

Las secciones son sugerencias; ajusta su numeración a los encabezados reales de
tu capítulo. Las figuras no llevan el pie incrustado, para que puedas añadirlo
con el formato de tu documento.

## Recursos y reproducibilidad

- Los 21 fondos del catálogo son SVG y están en `frontend/assets/images/`.
- `figura_01_catalogo_fondos.png` reúne los 21 fondos del catálogo.
- `figura_02_fondo.png` es una copia renderizada del SVG usado en la interfaz;
  el original se conserva sin cambios.
- `figura_03_interfaz_seleccion.png` es una captura de la interfaz web real con
  cinco puntos seleccionados.
- `figura_08_sistema_coordenadas.png` muestra la cuadrícula de coordenadas y
  los valores de la selección regular devuelta por la interfaz.
- Las figuras `figura_09_distribucion_agrupada.png`,
  `figura_10_distribucion_lineal.png` y
  `figura_11_distribucion_regular.png` son capturas de la interfaz real sobre
  el mismo fondo del catálogo.
- `seleccion_capitulo_2_analisis.json` contiene la respuesta JSON real del
  backend para la selección ilustrativa.
- `seleccion_agrupada_analisis.json`,
  `seleccion_lineal_analisis.json` y `seleccion_regular_analisis.json` guardan
  las respuestas del backend para las selecciones de las figuras 09–11.
- `generar_figuras_capitulo_2.py` genera las figuras 04–08 y verifica que los
  ángulos, perímetros y patrones coincidan con esas respuestas. Ejecútalo desde
  la raíz con el entorno del proyecto:

      .venv/bin/python -m docs.figuras.generar_figuras_capitulo_2

Las respuestas guardadas confirman las aristas de Delaunay, los ángulos,
perímetros y las clasificaciones comunicadas en los pies de figura. Para una
investigación con participantes, sustituye estos ejemplos controlados por
selecciones recopiladas con el protocolo aprobado; no los presentes como
evidencia experimental.

## Herramientas anteriores

`01_listar_imagenes.py` lista los archivos raster y SVG del proyecto.
`02_extraer_fondo.py` copia imágenes raster compatibles con Pillow como
`fondo_extraido.png`.
`03_dibujar_puntos.py` permite dibujar los puntos de un JSON con la propiedad
`points` sobre un fondo raster y guarda el resultado como `puntos_dibujados.png`.
