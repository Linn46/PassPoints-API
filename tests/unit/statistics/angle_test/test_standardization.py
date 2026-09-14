import pytest

from app.statistics.angle_test.normal_distribution import (
    AMADT_PARAMETERS,
)
from app.statistics.angle_test.standardization import (
    standardize,
)
from app.statistics.angle_test.statistic import (
    angle_statistic,
)


def test_reference_mean_produces_zero():
    result = standardize(
        AMADT_PARAMETERS.mean
    )

    assert result == pytest.approx(0.0)


def test_standardization_above_mean():
    result = standardize(129.0)

    expected = (
        129.0 - 111.8
    ) / 17.2

    assert result == pytest.approx(expected)


def test_angle_statistic_uses_standardization():
    result = angle_statistic(111.8)

    assert result == pytest.approx(0.0)