from app.statistics.angle_test.standardization import (
    standardize,
)


def angle_statistic(
    average_max_angle: float,
) -> float:
    """
    Calcula el estadístico Z del test basado en
    el promedio de los ángulos máximos.
    """

    return standardize(
        average_max_angle
    )