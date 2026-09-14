from app.domain.triangle import Triangle
from app.geometry.triangle.sides import triangle_side_lengths


class TriangleValidationError(ValueError):
    """Error producido cuando un triángulo no es válido."""


def validate_triangle(triangle: Triangle) -> None:
    """
    Valida las propiedades geométricas básicas de un triángulo.
    """

    a, b, c = triangle_side_lengths(triangle)

    if min(a, b, c) <= 0:
        raise TriangleValidationError(
            "Triangle sides must be greater than zero."
        )

    if a + b <= c or a + c <= b or b + c <= a:
        raise TriangleValidationError(
            "The triangle violates the triangle inequality."
        )