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
    """Interpreta los tests y relaciona cada contraseña con un patrón."""

    patterns: list[str] = []

    if perimeter_test.reject_null:
        if _points_are_grouped(
            points,
            image_width,
            image_height,
        ):
            patterns.append("Patrón agrupado")
        elif _triangles_are_regular(triangles):
            patterns.append("Patrón regular")
        else:
            patterns.append("Perímetros atípicos")

    if angle_test.reject_null:
        patterns.append(
            _angular_pattern(
                points,
                image_width,
                image_height,
            )
        )

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
    level = "Baja" if (
        len(patterns) > 1
        or "Patrón agrupado" in patterns
    ) else "Media"
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


def _triangles_are_regular(
    triangles: tuple[Triangle, ...],
) -> bool:
    perimeters = [
        triangle_perimeter(triangle)
        for triangle in triangles
    ]
    maximum_angles = [
        triangle_max_angle_degrees(triangle)
        for triangle in triangles
    ]

    if not perimeters or not maximum_angles:
        return False

    perimeter_variation = pstdev(perimeters) / (sum(perimeters) / len(perimeters))
    angle_variation = pstdev(maximum_angles) / (
        sum(maximum_angles) / len(maximum_angles)
    )

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
    first, second = max(
        (
            (first, second)
            for index, first in enumerate(points)
            for second in points[index + 1 :]
        ),
        key=lambda pair: math.hypot(
            pair[0].x - pair[1].x,
            pair[0].y - pair[1].y,
        ),
    )
    axis_angle = math.degrees(
        math.atan2(
            abs(second.y - first.y),
            abs(second.x - first.x),
        )
    )
    maximum_distance = math.hypot(
        second.x - first.x,
        second.y - first.y,
    )
    linearity_tolerance = min(image_width, image_height) * 0.1

    if all(
        abs(
            (second.x - first.x) * (point.y - first.y)
            - (second.y - first.y) * (point.x - first.x)
        )
        <= linearity_tolerance * maximum_distance
        for point in points
    ):
        if axis_angle <= 15 or axis_angle >= 75:
            return "Patrón Line"
        return "Patrón Diag"

    return "Patrón angular"