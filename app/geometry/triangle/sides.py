from app.domain.triangle import Triangle
from app.geometry.distance.euclidean import euclidean_distance


def triangle_side_lengths(
    triangle: Triangle,
) -> tuple[float, float, float]:
    """
    Calcula las longitudes de los tres lados de un triángulo.

    Retorna:
        (a, b, c)
    """
    first, second, third = triangle.vertices

    return (
        euclidean_distance(second, third),
        euclidean_distance(first, third),
        euclidean_distance(first, second),
    )