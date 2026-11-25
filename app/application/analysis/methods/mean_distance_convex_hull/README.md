# Tests DM, PEC y AEC

Implementación de los contrastes descritos por Herrera para contraseñas PassPoint
formadas por exactamente cinco puntos.

- **DM**: media de las diez distancias euclidianas por pares. Referencia normal:
  800x480 -> N(339, 71); 1366x768 -> N(568, 120); 1920x1080 -> N(798, 168).
  Contraste bilateral; cola izquierda asociada a agrupamiento y derecha a regularidad.
- **PEC**: perímetro de la envolvente convexa, transformación Johnson SB y contraste
  bilateral. Los parámetros publicados se limitan a 1920x1080. La cola izquierda se
  utiliza para detectar agrupamiento. Fuera del dominio Johnson SB, PEC no es evaluable.
- **AEC**: área de la envolvente convexa, distribución Weibull (forma 2.2478,
  escala 500760) y contraste bilateral por percentiles. Los parámetros publicados
  se limitan a 1920x1080; se utiliza la cola derecha para detectar regularidad.

La tesis reporta resultados experimentales no significativos para PEC en la detección
regular y AEC en la detección agrupada. Por eso estas colas no se utilizan para
clasificar patrones en esta implementación. No detectar un patrón no demuestra
aleatoriedad: significa que no se rechazó la hipótesis nula con los contrastes
aplicables.


### Interpretación estadística y límites de evidencia

Los contrastes PEC y AEC se definen formalmente con regiones críticas bilaterales.
Sin embargo, Herrera informa que la detección de regularidad mediante PEC y la
detección de agrupamiento mediante AEC no resultaron significativas en sus
experimentos. Por ello, el sistema solo atribuye patrón agrupado a la cola izquierda
de PEC y patrón regular a la cola derecha de AEC. Una observación puede caer en
la otra cola y rechazar formalmente H0 sin que el sistema le asigne un patrón
respaldado. Ese caso debe interpretarse como rechazo sin clasificación validada,
no como ausencia de rechazo ni como evidencia de aleatoriedad.

La fuente calibra PEC y AEC para 1920 × 1080. No se extrapolan esos parámetros
a otras resoluciones.


**Alcance de clasificación:** esta implementación no clasifica el patrón lineal (Line). DM, PEC y AEC se emplean únicamente para las categorías agrupado y regular en las regiones con respaldo experimental descrito arriba. No se debe interpretar la ausencia de detección como aleatoriedad.
