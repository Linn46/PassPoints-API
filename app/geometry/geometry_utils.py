from math import hypot

from app.domain.point import Point


def cross_product(
    origin: Point,
    first: Point,
    second: Point,
) -> float:
    """Calcula el producto cruzado 2D de los vectores desde ``origin``."""
    return (
        (first.x - origin.x) * (second.y - origin.y)
        - (first.y - origin.y) * (second.x - origin.x)
    )


def are_collinear(
    first: Point,
    second: Point,
    third: Point,
    tolerance: float = 1e-12,
) -> bool:
    """Determina colinealidad usando una tolerancia angular relativa.

    La comparación relativa evita que el resultado dependa de la escala de
    las coordenadas. ``tolerance`` aproxima el seno mínimo del ángulo entre
    los vectores; no representa una distancia en píxeles.
    """
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    first_length = hypot(first.x - second.x, first.y - second.y)
    second_length = hypot(first.x - third.x, first.y - third.y)
    determinant = abs(cross_product(first, second, third))

    if first_length == 0 or second_length == 0:
        return True

    return determinant <= tolerance * first_length * second_length
