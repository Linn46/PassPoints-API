from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    """
    Representa un punto de coordenadas (x, y) dentro de la imagen.
    """

    x: float
    y: float