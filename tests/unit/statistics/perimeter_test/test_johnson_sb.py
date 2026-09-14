import pytest
import math

from app.statistics.perimeter_test.johnson_sb import (
    PARAMETERS_BY_IMAGE_SIZE,
)
from app.statistics.perimeter_test.transformation import (
    JohnsonSBTransformationError,
    transform,
)


def test_1920x1080_parameters():
    parameters = PARAMETERS_BY_IMAGE_SIZE[(1920, 1080)]

    assert parameters.gamma == pytest.approx(-0.21458)
    assert parameters.delta == pytest.approx(2.0283)
    assert parameters.lambda_ == pytest.approx(3940.5)
    assert parameters.xi == pytest.approx(-30.961)


def test_johnson_sb_transformation():
    parameters = PARAMETERS_BY_IMAGE_SIZE[(1920, 1080)]

    result = transform(2000.0, parameters)

    assert math.isfinite(result)


def test_johnson_sb_rejects_value_outside_domain():
    parameters = PARAMETERS_BY_IMAGE_SIZE[(1920, 1080)]

    with pytest.raises(JohnsonSBTransformationError):
        transform(parameters.xi, parameters)