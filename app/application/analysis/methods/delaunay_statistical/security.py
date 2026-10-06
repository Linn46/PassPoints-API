import math
from statistics import pstdev

from app.domain.point import Point
from app.domain.security_assessment import SecurityAssessment
from app.domain.triangle import Triangle
from app.geometry.triangle.angles import triangle_max_angle_degrees
from app.geometry.triangle.perimeter import triangle_perimeter
from app.statistics.angle_test.test import AngleTestResult
from app.statistics.perimeter_test.test import PerimeterTestStatistic


def assess_security(
    perimeter_test: PerimeterTestStatistic,
    angle_test: AngleTestResult,
    points: list[Point],
    triangles: tuple[Triangle, ...],
    image_width: int,
    image_height: int,
) -> SecurityAssessment:
    """Interpreta los tests del método Delaunay y clasifica la seguridad."""

    patterns: list[str] = []
    angular_pattern = (
        _angular_pattern(points, image_width, image_height) if angle_test.reject_null else None
    )

    if perimeter_test.reject_null:
        if _points_are_grouped(points, image_width, image_height):
            patterns.append("Patrón agrupado")
        elif (
            angular_pattern not in {"Patrón Line", "Patrón Diag"}
            and _triangles_are_regular(triangles)
        ):
            patterns.append("Patrón regular")

    if angular_pattern is not None:
        patterns.append(angular_pattern)

    if not patterns:
        return SecurityAssessment(
            is_weak=False,
            level="Alta",
            patterns=[],
            title="Contraseña sin patrón débil detectado",
            explanation=(
                "No se detectó un patrón geométrico no aleatorio con los "
                "criterios utilizados por el análisis."
            ),
        )

    pattern_text = ", ".join(patterns)
    level = "Baja" if len(patterns) > 1 or "Patrón agrupado" in patterns else "Media"
    evidence = []

    if perimeter_test.reject_null:
        evidence.append(
            "el test de perímetros rechazó H0 "
            f"(Z={perimeter_test.statistic:.2f})"
        )

    if angle_test.reject_null:
        evidence.append(
            "el test de ángulos rechazó H0 "
            f"(Z={angle_test.statistic:.2f})"
        )

    return SecurityAssessment(
        is_weak=True,
        level=level,
        patterns=patterns,
        title="Contraseña no segura",
        explanation=(
            "Los puntos seleccionados presentan características compatibles "
            f"con {pattern_text}. La decisión se basa en que "
            f"{_join_evidence(evidence)}."
        ),
    )


def _join_evidence(evidence: list[str]) -> str:
    if len(evidence) == 1:
        return evidence[0]
    return " y ".join(evidence)


def _triangles_are_regular(triangles: tuple[Triangle, ...]) -> bool:
    perimeters = [triangle_perimeter(triangle) for triangle in triangles]
    maximum_angles = [triangle_max_angle_degrees(triangle) for triangle in triangles]

    if not perimeters or not maximum_angles:
        return False

    average_perimeter = sum(perimeters) / len(perimeters)
    average_angle = sum(maximum_angles) / len(maximum_angles)

    if average_perimeter <= 0 or average_angle <= 0:
        return False

    perimeter_variation = pstdev(perimeters) / average_perimeter
    angle_variation = pstdev(maximum_angles) / average_angle

    return perimeter_variation <= 0.1 and angle_variation <= 0.1


def _points_are_grouped(
    points: list[Point],
    image_width: int,
    image_height: int,
) -> bool:
    maximum_distance = max(
        math.hypot(first.x - second.x, first.y - second.y)
        for index, first in enumerate(points)
        for second in points[index + 1 :]
    )
    grouping_distance = min(image_width, image_height) * 0.25

    return maximum_distance <= grouping_distance


def _angular_pattern(
    points: list[Point],
    image_width: int,
    image_height: int,
) -> str:
    center_x = sum(point.x for point in points) / len(points)
    center_y = sum(point.y for point in points) / len(points)
    covariance_xx = sum((point.x - center_x) ** 2 for point in points)
    covariance_yy = sum((point.y - center_y) ** 2 for point in points)
    covariance_xy = sum((point.x - center_x) * (point.y - center_y) for point in points)
    principal_angle = 0.5 * math.atan2(
        2 * covariance_xy,
        covariance_xx - covariance_yy,
    )
    direction_x = math.cos(principal_angle)
    direction_y = math.sin(principal_angle)
    projections = [
        (point.x - center_x) * direction_x + (point.y - center_y) * direction_y
        for point in points
    ]
    minimum_projection = min(projections)
    maximum_projection = max(projections)
    span = maximum_projection - minimum_projection

    if span <= 0:
        return "Patrón angular"

    perpendicular_rms = math.sqrt(
        sum(
            (
                -(point.x - center_x) * direction_y
                + (point.y - center_y) * direction_x
            ) ** 2
            for point in points
        )
        / len(points)
    )
    linearity_tolerance = min(image_width, image_height) * 0.1

    if perpendicular_rms <= linearity_tolerance:
        first = points[projections.index(minimum_projection)]
        second = points[projections.index(maximum_projection)]
        axis_angle = math.degrees(
            math.atan2(
                abs(second.y - first.y),
                abs(second.x - first.x),
            )
        )
        slope_direction = (second.y - first.y) * (second.x - first.x)

        if axis_angle <= 15 or axis_angle >= 75:
            return "Patrón Line"
        if slope_direction > 0:
            return "Patrón Line"
        return "Patrón Diag"

    return "Patrón angular"
