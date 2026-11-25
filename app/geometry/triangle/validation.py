from app.domain.triangle import Triangle
from app.geometry.geometry_utils import are_collinear
from app.geometry.triangle.sides import triangle_side_lengths


class TriangleValidationError(ValueError):
    """Error producido cuando un triángulo no es geométricamente válido."""


def validate_triangle(triangle: Triangle) -> None:
    """Rechaza triángulos con lados nulos o vértices colineales/casi colineales."""
    a, b, c = triangle_side_lengths(triangle)

    if min(a, b, c) <= 0:
        raise TriangleValidationError("Triangle sides must be greater than zero.")

    if are_collinear(*triangle.vertices):
        raise TriangleValidationError(
            "Triangle vertices must not be collinear or nearly collinear."
        )

    if a + b <= c or a + c <= b or b + c <= a:
        raise TriangleValidationError("The triangle violates the triangle inequality.")
