import pytest

from app.statistics.angle_test.critical_region import (
    critical_value,
    is_in_critical_region,
)
from app.statistics.angle_test.test import run_test


def test_critical_value_alpha_005():
    result = critical_value(0.05)

    assert result == pytest.approx(
        1.644853,
        abs=1e-5,
    )


def test_critical_value_alpha_001():
    result = critical_value(0.01)

    assert result == pytest.approx(
        2.326348,
        abs=1e-5,
    )


def test_statistic_inside_right_critical_region():
    assert is_in_critical_region(
        2.0,
        0.05,
    )


def test_statistic_outside_right_critical_region():
    assert not is_in_critical_region(
        1.0,
        0.05,
    )


def test_negative_statistic_is_not_in_critical_region():
    assert not is_in_critical_region(
        -2.0,
        0.05,
    )


def test_angle_test_rejects_null():
    result = run_test(
        average_max_angle=150.0,
        alpha=0.05,
    )

    assert result.statistic > result.critical_value
    assert result.reject_null is True


def test_angle_test_does_not_reject_null():
    result = run_test(
        average_max_angle=111.8,
        alpha=0.05,
    )

    assert result.statistic == pytest.approx(0.0)
    assert result.reject_null is False