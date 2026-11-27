import pytest

from app.domain.point import Point
from app.domain.triangle import Triangle
from app.geometry.delaunay.converter import points_from_coordinates
from app.geometry.delaunay.triangulator import triangulate
from app.geometry.delaunay.validator import DelaunayValidationError
from app.geometry.geometry_utils import (
    are_collinear,
    cross_product,
)
from app.geometry.triangle.validation import (
    TriangleValidationError,
    validate_triangle,
)


def valid_points() -> list[Point]:
    return [
        Point(0, 0),
        Point(10, 0),
        Point(10, 10),
        Point(0, 10),
        Point(5, 5),
    ]


def test_converter_creates_points():
    coordinates = [
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
        (5, 5),
    ]

    points = points_from_coordinates(coordinates)

    assert len(points) == 5
    assert points[0] == Point(0, 0)
    assert points[4] == Point(5, 5)


def test_delaunay_creates_triangles():
    triangulation = triangulate(valid_points())

    assert len(triangulation.triangles) > 0

    for triangle in triangulation.triangles:
        assert len(triangle.vertices) == 3


def test_delaunay_rejects_wrong_number_of_points():
    points = valid_points()[:4]

    with pytest.raises(DelaunayValidationError):
        triangulate(points)


def test_cross_product_for_counterclockwise_points():
    result = cross_product(
        Point(0, 0),
        Point(1, 0),
        Point(1, 1),
    )

    assert result > 0


def test_collinear_points():
    assert are_collinear(
        Point(0, 0),
        Point(1, 1),
        Point(2, 2),
    )


def test_non_collinear_points():
    assert not are_collinear(
        Point(0, 0),
        Point(1, 0),
        Point(1, 1),
    )


def test_valid_triangle():
    triangle = Triangle(
        (
            Point(0, 0),
            Point(3, 0),
            Point(0, 4),
        )
    )

    validate_triangle(triangle)


def test_invalid_triangle():
    triangle = Triangle(
        (
            Point(0, 0),
            Point(1, 0),
            Point(2, 0),
        )
    )

    with pytest.raises(TriangleValidationError):
        validate_triangle(triangle)

def test_triangulation_rejects_nearly_collinear_points():
    points = [
        Point(0, 0),
        Point(1, 0),
        Point(2, 1e-14),
        Point(3, 0),
        Point(4, 0),
    ]

    with pytest.raises(DelaunayValidationError) as exc_info:
        triangulate(points)

    assert exc_info.value.validation_type == "collinear_points"


def test_delaunay_output_is_repeatable_for_same_input():
    points = valid_points()

    first = triangulate(points)
    second = triangulate(points)

    assert first == second


def test_cocircular_permutations_produce_valid_covering_triangulations():
    """Cocircular inputs may admit different diagonals; validate geometry, not identity."""
    from itertools import permutations
    from math import cos, pi, sin

    points = [
        Point(100 * cos(2 * pi * index / 5), 100 * sin(2 * pi * index / 5))
        for index in range(5)
    ]

    def polygon_area(vertices):
        return abs(sum(
            vertices[i].x * vertices[(i + 1) % len(vertices)].y
            - vertices[(i + 1) % len(vertices)].x * vertices[i].y
            for i in range(len(vertices))
        )) / 2

    expected_area = polygon_area(points)
    for ordering in permutations(points):
        result = triangulate(list(ordering))
        assert len(result.triangles) == 3
        triangle_area = sum(
            abs(
                (t.vertices[1].x - t.vertices[0].x)
                * (t.vertices[2].y - t.vertices[0].y)
                - (t.vertices[2].x - t.vertices[0].x)
                * (t.vertices[1].y - t.vertices[0].y)
            ) / 2
            for t in result.triangles
        )
        assert triangle_area == pytest.approx(expected_area, rel=1e-8)
