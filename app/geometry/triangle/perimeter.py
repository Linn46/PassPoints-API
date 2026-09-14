from app.domain.triangle import Triangle
from app.geometry.triangle.sides import triangle_side_lengths


def triangle_perimeter(triangle: Triangle) -> float:
    """
    Calcula el perímetro de un triángulo.
    """
    a, b, c = triangle_side_lengths(triangle)

    return a + b + c


def average_delaunay_perimeter(
    triangles: tuple[Triangle, ...],
) -> float:
    """
    Calcula el promedio de los perímetros de los triángulos
    de una triangulación de Delaunay.
    """
    if not triangles:
        raise ValueError(
            "At least one Delaunay triangle is required."
        )

    total = sum(
        triangle_perimeter(triangle)
        for triangle in triangles
    )

    return total / len(triangles)