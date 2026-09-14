from app.domain.point import Point


def points_from_coordinates(
    coordinates: list[tuple[float, float]],
) -> list[Point]:
    """
    Convierte coordenadas simples (x, y) en objetos Point.
    """
    return [
        Point(x=x, y=y)
        for x, y in coordinates
    ]