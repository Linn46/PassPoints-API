from app.domain.point import Point


class DelaunayValidationError(ValueError):
    """
    Error producido cuando los puntos no son válidos
    para realizar la triangulación.
    """
    def __init__(self, message: str, validation_type: str = "unknown", details: dict = None):
        self.message = message
        self.validation_type = validation_type
        self.details = details or {}
        super().__init__(self.message)


def validate_points(points: list[Point]) -> None:
    """
    Valida los puntos de entrada para la triangulación.
    
    Raises:
        DelaunayValidationError: If points don't meet validation requirements
    """

    if len(points) != 5:
        raise DelaunayValidationError(
            "A PassPoints password must contain exactly five points.",
            validation_type="point_count",
            details={"expected": 5, "received": len(points)}
        )

    if len(set(points)) != 5:
        duplicate_indices = _find_duplicates(points)
        raise DelaunayValidationError(
            "The five points must be unique. Duplicate points detected.",
            validation_type="duplicate_points",
            details={"duplicate_indices": duplicate_indices}
        )

    for i in range(1, 4):
        for j in range(i + 1, 5):
            cross_product = (
                (points[i].x - points[0].x)
                * (points[j].y - points[0].y)
                - (points[i].y - points[0].y)
                * (points[j].x - points[0].x)
            )

            if cross_product != 0:
                return

    raise DelaunayValidationError(
        "The five points cannot be collinear. Points must form a non-degenerate triangle.",
        validation_type="collinear_points",
        details={"all_points": [(p.x, p.y) for p in points]}
    )


def _find_duplicates(points: list[Point]) -> list[tuple[int, int]]:
    """Find indices of duplicate points."""
    duplicates = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if points[i] == points[j]:
                duplicates.append((i, j))
    return duplicates