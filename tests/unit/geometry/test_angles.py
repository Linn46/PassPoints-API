import pytest

from app.domain.point import Point
from app.domain.triangle import Triangle
from app.geometry.triangle.angles import (
    average_max_delaunay_angle,
    triangle_angles_degrees,
    triangle_max_angle_degrees,
)


def right_triangle() -> Triangle:
    return Triangle(
        (
            Point(0, 0),
            Point(3, 0),
            Point(0, 4),
        )
    )


def test_triangle_angles():
    triangle = right_triangle()

    angles = triangle_angles_degrees(triangle)

    assert angles[0] == pytest.approx(90.0)
    assert angles[1] == pytest.approx(
        53.130102354
    )
    assert angles[2] == pytest.approx(
        36.869897646
    )


def test_triangle_angles_sum_180():
    triangle = right_triangle()

    angles = triangle_angles_degrees(triangle)

    assert sum(angles) == pytest.approx(180.0)


def test_triangle_max_angle():
    triangle = right_triangle()

    maximum = triangle_max_angle_degrees(triangle)

    assert maximum == pytest.approx(90.0)


def test_average_max_delaunay_angle():
    triangle = right_triangle()

    average = average_max_delaunay_angle(
        (triangle, triangle)
    )

    assert average == pytest.approx(90.0)