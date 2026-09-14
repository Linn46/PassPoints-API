from math import acos, degrees

from app.domain.triangle import Triangle
from app.geometry.triangle.sides import triangle_side_lengths


def _safe_acos(value: float) -> float:
    """
    Limita el valor al intervalo [-1, 1] antes de aplicar acos,
    evitando errores producidos por redondeo numérico.
    """
    return acos(max(-1.0, min(1.0, value)))


def triangle_angles_degrees(
    triangle: Triangle,
) -> tuple[float, float, float]:
    """
    Calcula los tres ángulos interiores de un triángulo
    y los devuelve en grados.
    """
    a, b, c = triangle_side_lengths(triangle)

    angle_a = degrees(
        _safe_acos(
            (b**2 + c**2 - a**2) / (2 * b * c)
        )
    )

    angle_b = degrees(
        _safe_acos(
            (a**2 + c**2 - b**2) / (2 * a * c)
        )
    )

    angle_c = degrees(
        _safe_acos(
            (a**2 + b**2 - c**2) / (2 * a * b)
        )
    )

    return angle_a, angle_b, angle_c


def triangle_max_angle_degrees(
    triangle: Triangle,
) -> float:
    """
    Devuelve el mayor de los tres ángulos interiores.
    """
    return max(triangle_angles_degrees(triangle))


def average_max_delaunay_angle(
    triangles: tuple[Triangle, ...],
) -> float:
    """
    Calcula el promedio de los ángulos máximos de los triángulos
    de una triangulación de Delaunay.
    """
    if not triangles:
        raise ValueError(
            "At least one Delaunay triangle is required."
        )

    total = sum(
        triangle_max_angle_degrees(triangle)
        for triangle in triangles
    )

    return total / len(triangles)