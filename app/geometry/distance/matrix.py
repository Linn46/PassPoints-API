from math import hypot

from app.domain.point import Point


def distance_matrix(points: list[Point]) -> list[list[float]]:
    """
    Calcula la matriz de distancias euclidianas entre todos los puntos.
    """
    return [
        [
            hypot(
                first.x - second.x,
                first.y - second.y,
            )
            for second in points
        ]
        for first in points
    ]