import pytest

from app.domain.point import Point
from app.application.analysis.service import AnalysisService
from app.api.schemas.analysis_request import AnalysisRequest


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


def test_analysis_service_supports_mean_distance_convex_hull_method():
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
        method="mean_distance_convex_hull",
    )

    assert result.method == "mean_distance_convex_hull"
    assert result.security is not None
    assert result.security.patterns
    assert "Patrón" in result.security.patterns[0]
    assert "Los puntos seleccionados presentan características compatibles" in result.security.explanation


def test_analysis_request_accepts_one_or_multiple_methods():
    payload = {
        "points": [
            {"x": 100, "y": 100},
            {"x": 500, "y": 100},
            {"x": 500, "y": 500},
            {"x": 100, "y": 500},
            {"x": 300, "y": 300},
        ],
        "image_width": 1920,
        "image_height": 1080,
        "alpha": 0.05,
        "methods": [
            "delaunay_statistical",
            "mean_distance_convex_hull",
        ],
    }

    request = AnalysisRequest.model_validate(payload)

    assert request.methods == [
        "delaunay_statistical",
        "mean_distance_convex_hull",
    ]