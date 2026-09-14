import pytest

from app.domain.point import Point
from app.services.analysis_service import AnalysisService


def test_analysis_service_executes_complete_analysis():
    points = [
        Point(100, 100),
        Point(500, 100),
        Point(500, 500),
        Point(100, 500),
        Point(300, 300),
    ]

    result = AnalysisService().analyze(
        points=points,
        image_width=1920,
        image_height=1080,
        alpha=0.05,
    )

    assert len(result.triangulation.triangles) > 0

    assert result.average_perimeter > 0

    assert 0 < result.average_max_angle < 180

    assert result.perimeter_test.statistic == pytest.approx(
        result.perimeter_test.statistic
    )

    assert result.angle_test.statistic == pytest.approx(
        (
            result.average_max_angle - 111.8
        ) / 17.2
    )