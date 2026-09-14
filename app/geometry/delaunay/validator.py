from app.domain.point import Point


class DelaunayValidationError(ValueError):
    """
    Error producido cuando los puntos no son válidos
    para realizar la triangulación.
    """


def validate_points(points: list[Point]) -> None:
    """
    Valida los puntos de entrada para la triangulación.
    """

    if len(points) != 5:
        raise DelaunayValidationError(
            "A PassPoints password must contain exactly five points."
        )

    if len(set(points)) != 5:
        raise DelaunayValidationError(
            "The five points must be unique."
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
        "The five points cannot be collinear."
    )