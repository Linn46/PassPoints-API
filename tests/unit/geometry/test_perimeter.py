import pytest

from app.domain.point import Point
from app.domain.triangle import Triangle
from app.geometry.triangle.perimeter import (
    average_delaunay_perimeter,
    triangle_perimeter,
)
from app.geometry.triangle.sides import triangle_side_lengths


def right_triangle() -> Triangle:
    return Triangle(
        (
            Point(0, 0),
            Point(3, 0),
            Point(0, 4),
        )
    )


def test_triangle_side_lengths():
    triangle = right_triangle()

    sides = triangle_side_lengths(triangle)

    assert sides[0] == pytest.approx(5.0)
    assert sides[1] == pytest.approx(4.0)
    assert sides[2] == pytest.approx(3.0)


def test_triangle_perimeter():
    triangle = right_triangle()

    perimeter = triangle_perimeter(triangle)

    assert perimeter == pytest.approx(12.0)


def test_average_delaunay_perimeter():
    triangle = right_triangle()

    average = average_delaunay_perimeter(
        (triangle, triangle)
    )

    assert average == pytest.approx(12.0)