from app.statistics.perimeter_test.statistic import (
    PerimeterTestStatistic,
    evaluate,
)


DEFAULT_ALPHA = 0.05


def run_test(
    average_perimeter: float,
    image_width: int,
    image_height: int,
    alpha: float = DEFAULT_ALPHA,
) -> PerimeterTestStatistic:
    """
    Ejecuta el test de aleatoriedad basado en el promedio
    de los perímetros de los triángulos de Delaunay.
    """

    return evaluate(
        average_perimeter=average_perimeter,
        image_width=image_width,
        image_height=image_height,
        alpha=alpha,
    )