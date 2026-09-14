from app.statistics.angle_test.normal_distribution import (
    AMADT_PARAMETERS,
)


def standardize(
    average_max_angle: float,
) -> float:
    """
    Estandariza el promedio de los ángulos máximos
    respecto a la distribución normal de referencia.

    Z = (X̄ - μ) / σ
    """

    return (
        average_max_angle - AMADT_PARAMETERS.mean
    ) / AMADT_PARAMETERS.standard_deviation