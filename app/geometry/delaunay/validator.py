from app.domain.point import Point
from app.geometry.geometry_utils import are_collinear


class DelaunayValidationError(ValueError):
    """Error producido cuando los puntos no son válidos para Delaunay."""

    def __init__(self, message: str, validation_type: str = "unknown", details: dict = None):
        self.message = message
        self.validation_type = validation_type
        self.details = details or {}
        super().__init__(self.message)


def validate_points(points: list[Point]) -> None:
    """Valida cantidad, unicidad y no-colinealidad de los cinco puntos."""
    if len(points) != 5:
        raise DelaunayValidationError(
            "A PassPoints password must contain exactly five points.",
            validation_type="point_count",
            details={"expected": 5, "received": len(points)},
        )

    if len(set(points)) != 5:
        raise DelaunayValidationError(
            "The five points must be unique. Duplicate points detected.",
            validation_type="duplicate_points",
            details={"duplicate_indices": _find_duplicates(points)},
        )

    origin = points[0]
    for first_index in range(1, 4):
        for second_index in range(first_index + 1, 5):
            if not are_collinear(origin, points[first_index], points[second_index]):
                return

    raise DelaunayValidationError(
        "The five points cannot be collinear. Points must form a non-degenerate triangle.",
        validation_type="collinear_points",
        details={"all_points": [(point.x, point.y) for point in points]},
    )


def _find_duplicates(points: list[Point]) -> list[tuple[int, int]]:
    """Devuelve los pares de índices que contienen puntos duplicados."""
    duplicates = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if points[i] == points[j]:
                duplicates.append((i, j))
    return duplicates
