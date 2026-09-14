import math

from app.statistics.perimeter_test.johnson_sb import (
    JohnsonSBParameters,
)


class JohnsonSBTransformationError(ValueError):
    """Error producido al aplicar una transformación Johnson SB inválida."""


def transform(
    value: float,
    parameters: JohnsonSBParameters,
) -> float:
    """
    Transforma un valor mediante Johnson SB.

    Z = gamma + delta * ln(
        (value - xi) /
        (lambda + xi - value)
    )
    """

    numerator = value - parameters.xi
    denominator = (
        parameters.lambda_
        + parameters.xi
        - value
    )

    if numerator <= 0 or denominator <= 0:
        raise JohnsonSBTransformationError(
            "The value is outside the Johnson SB domain."
        )

    return parameters.gamma + parameters.delta * math.log(
        numerator / denominator
    )