from app.domain.point import Point


def cross_product(
    origin: Point,
    first: Point,
    second: Point,
) -> float:
    """
    Calcula el producto cruzado 2D de los vectores:

        origin -> first
        origin -> second

    Un resultado:
        > 0 : orientación antihoraria
        < 0 : orientación horaria
        = 0 : puntos colineales
    """

    return (
        (first.x - origin.x) * (second.y - origin.y)
        - (first.y - origin.y) * (second.x - origin.x)
    )


def are_collinear(
    first: Point,
    second: Point,
    third: Point,
    tolerance: float = 1e-12,
) -> bool:
    """
    Determina si tres puntos son aproximadamente colineales.
    """

    return abs(
        cross_product(first, second, third)
    ) <= tolerance