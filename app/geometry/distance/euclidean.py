from math import hypot

from app.domain.point import Point


def euclidean_distance(first: Point, second: Point) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos.
    """
    return hypot(
        first.x - second.x,
        first.y - second.y,
    )