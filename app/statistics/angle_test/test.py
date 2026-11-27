from dataclasses import dataclass

from app.statistics.angle_test.critical_region import (
    critical_value,
    is_in_critical_region,
)
from app.statistics.angle_test.statistic import angle_statistic


DEFAULT_ALPHA = 0.05


@dataclass(frozen=True, slots=True)
class AngleTestResult:
    """
    Resultado del test basado en el promedio de los
    ángulos máximos de los triángulos de Delaunay.
    """

    average_max_angle: float
    statistic: float
    critical_value: float
    alpha: float
    reject_null: bool
    applicable: bool = True


def run_test(
    average_max_angle: float,
    alpha: float = DEFAULT_ALPHA,
    image_width: int = 1920,
    image_height: int = 1080,
) -> AngleTestResult:
    """
    Ejecuta el test unilateral derecho para detectar
    patrones Diag y Line.
    """

    statistic = angle_statistic(average_max_angle)
    critical = critical_value(alpha)
    applicable = (image_width, image_height) == (1920, 1080)

    return AngleTestResult(
        average_max_angle=average_max_angle,
        statistic=statistic,
        critical_value=critical,
        alpha=alpha,
        reject_null=(applicable and is_in_critical_region(statistic, alpha)),
        applicable=applicable,
    )