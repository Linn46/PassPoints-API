import math

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

    if not math.isfinite(average_max_angle):
        raise ValueError("average_max_angle must be finite.")

    if AMADT_PARAMETERS.standard_deviation <= 0:
        raise ValueError("The reference standard deviation must be positive.")

    return (
        average_max_angle - AMADT_PARAMETERS.mean
    ) / AMADT_PARAMETERS.standard_deviation
