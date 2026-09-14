import pytest

from app.statistics.perimeter_test.critical_region import (
    critical_value,
    is_in_critical_region,
)
from app.statistics.perimeter_test.test import run_test


def test_critical_value_for_alpha_005():
    result = critical_value(0.05)

    assert result == pytest.approx(1.959964, abs=1e-5)


def test_statistic_inside_critical_region():
    assert is_in_critical_region(2.0, 0.05)


def test_statistic_outside_critical_region():
    assert not is_in_critical_region(1.0, 0.05)


def test_negative_statistic_inside_critical_region():
    assert is_in_critical_region(-2.0, 0.05)


def test_perimeter_test_returns_decision():
    result = run_test(
        average_perimeter=3702.9,
        image_width=1920,
        image_height=1080,
        alpha=0.01,
    )

    assert result.statistic == pytest.approx(
        5.6558,
        abs=1e-3,
    )

    assert result.critical_value == pytest.approx(
        2.5758,
        abs=1e-3,
    )

    assert result.reject_null is True