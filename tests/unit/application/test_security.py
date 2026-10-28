from app.application.analysis.security import assess_security
from app.domain.point import Point
from app.geometry.delaunay.triangulator import triangulate
from app.statistics.angle_test.test import AngleTestResult
from app.statistics.perimeter_test.test import PerimeterTestStatistic


def perimeter_test(reject_null: bool, statistic: float):
    return PerimeterTestStatistic(
        statistic=statistic,
        critical_value=1.96,
        alpha=0.05,
        reject_null=reject_null,
    )


def points():
    return [
        Point(100, 100),
        Point(500, 100),
        Point(500, 500),
        Point(100, 500),
        Point(300, 300),
    ]


def grouped_points():
    return [
        Point(100, 100),
        Point(140, 100),
        Point(140, 140),
        Point(100, 140),
        Point(120, 120),
    ]


def triangles_for(points):
    return triangulate(points).triangles


def angle_test(reject_null: bool):
    return AngleTestResult(
        average_max_angle=150.0,
        statistic=2.0,
        critical_value=1.64,
        alpha=0.05,
        reject_null=reject_null,
    )


def test_rejected_low_perimeter_statistic_is_grouped_pattern():
    result = assess_security(
        perimeter_test=perimeter_test(True, -2.1),
        angle_test=angle_test(False),
        points=grouped_points(),
        triangles=triangles_for(grouped_points()),
        image_width=1920,
        image_height=1080,
    )

    assert result.is_weak is True
    assert result.level == "Baja"
    assert result.patterns == ["Patrón agrupado"]


def test_rejected_high_perimeter_statistic_is_regular_pattern():
    result = assess_security(
        perimeter_test=perimeter_test(True, 2.1),
        angle_test=angle_test(False),
        points=points(),
        triangles=triangles_for(points()),
        image_width=1920,
        image_height=1080,
    )

    assert result.patterns == ["Patrón regular"]
    assert result.level == "Media"


def test_rejected_angle_test_reports_one_pattern():
    result = assess_security(
        perimeter_test=perimeter_test(False, 0.0),
        angle_test=angle_test(True),
        points=points(),
        triangles=triangles_for(points()),
        image_width=1920,
        image_height=1080,
    )

    assert result.patterns == ["Patrón angular"]
    assert result.level == "Media"


def test_no_rejected_test_is_high_security_without_pattern():
    result = assess_security(
        perimeter_test=perimeter_test(False, 0.0),
        angle_test=angle_test(False),
        points=points(),
        triangles=triangles_for(points()),
        image_width=1920,
        image_height=1080,
    )

    assert result.is_weak is False
    assert result.level == "Alta"
    assert result.patterns == []
    assert "No se detectó" in result.explanation


def test_rejected_angle_test_identifies_line_pattern():
    line_points = [
        Point(100, 300),
        Point(350, 315),
        Point(650, 290),
        Point(950, 325),
        Point(1300, 300),
    ]
    result = assess_security(
        perimeter_test=perimeter_test(False, 0.0),
        angle_test=angle_test(True),
        points=line_points,
        triangles=triangles_for(line_points),
        image_width=1920,
        image_height=1080,
    )

    assert result.patterns == ["Patrón Line"]
    assert result.is_weak is True


def test_independent_rejections_report_multiple_patterns_and_low_security():
    result = assess_security(
        perimeter_test=perimeter_test(True, 2.1),
        angle_test=angle_test(True),
        points=points(),
        triangles=triangles_for(points()),
        image_width=1920,
        image_height=1080,
    )

    assert result.patterns == ["Patrón regular", "Patrón angular"]
    assert result.level == "Baja"
    assert [detail.pattern_id for detail in result.pattern_details] == [
        "regular",
        "angular",
    ]


def test_grouping_and_angle_detection_are_both_reported():
    selected_points = grouped_points()
    result = assess_security(
        perimeter_test=perimeter_test(True, -2.1),
        angle_test=angle_test(True),
        points=selected_points,
        triangles=triangles_for(selected_points),
        image_width=1920,
        image_height=1080,
    )

    assert "Patrón agrupado" in result.patterns
    assert any(
        pattern in result.patterns
        for pattern in ("Patrón Line", "Patrón Diag", "Patrón angular")
    )
    assert len(result.pattern_details) >= 2


def test_rejected_perimeter_without_geometric_pattern_is_not_weak():
    irregular_points = [
        Point(214, 173),
        Point(843, 921),
        Point(1472, 284),
        Point(1165, 735),
        Point(521, 492),
    ]
    result = assess_security(
        perimeter_test=perimeter_test(True, -2.1),
        angle_test=angle_test(False),
        points=irregular_points,
        triangles=triangles_for(irregular_points),
        image_width=1920,
        image_height=1080,
    )

    assert result.is_weak is False
    assert result.patterns == []