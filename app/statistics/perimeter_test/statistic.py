from dataclasses import dataclass

from app.statistics.perimeter_test.critical_region import (
    critical_value,
    is_in_critical_region,
)
from app.statistics.perimeter_test.johnson_sb import (
    PARAMETERS_BY_IMAGE_SIZE,
)
from app.statistics.perimeter_test.transformation import transform


@dataclass(frozen=True, slots=True)
class PerimeterTestStatistic:
    """
    Resultado del cálculo estadístico del test de perímetros.
    """

    statistic: float
    critical_value: float
    alpha: float
    reject_null: bool


def calculate_statistic(
    average_perimeter: float,
    image_width: int,
    image_height: int,
) -> float:
    """
    Calcula Z = JSB(P_D) utilizando los parámetros
    correspondientes al tamaño de la imagen.
    """

    try:
        parameters = PARAMETERS_BY_IMAGE_SIZE[
            (image_width, image_height)
        ]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported image size: "
            f"{image_width}x{image_height}."
        ) from exc

    return transform(
        average_perimeter,
        parameters,
    )


def evaluate(
    average_perimeter: float,
    image_width: int,
    image_height: int,
    alpha: float,
) -> PerimeterTestStatistic:
    """
    Ejecuta el cálculo estadístico y aplica el criterio
    de decisión del test bilateral.
    """

    statistic = calculate_statistic(
        average_perimeter,
        image_width,
        image_height,
    )

    critical = critical_value(alpha)

    return PerimeterTestStatistic(
        statistic=statistic,
        critical_value=critical,
        alpha=alpha,
        reject_null=is_in_critical_region(
            statistic,
            alpha,
        ),
    )