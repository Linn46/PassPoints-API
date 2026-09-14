import pytest

from app.domain.point import Point
from app.geometry.distance.euclidean import euclidean_distance
from app.geometry.distance.matrix import distance_matrix


def test_euclidean_distance():
    first = Point(0, 0)
    second = Point(3, 4)

    result = euclidean_distance(first, second)

    assert result == pytest.approx(5.0)


def test_euclidean_distance_is_symmetric():
    first = Point(0, 0)
    second = Point(3, 4)

    assert euclidean_distance(first, second) == pytest.approx(
        euclidean_distance(second, first)
    )


def test_distance_matrix():
    points = [
        Point(0, 0),
        Point(3, 4),
        Point(3, 0),
    ]

    matrix = distance_matrix(points)

    assert matrix[0][0] == pytest.approx(0.0)
    assert matrix[1][1] == pytest.approx(0.0)
    assert matrix[2][2] == pytest.approx(0.0)

    assert matrix[0][1] == pytest.approx(5.0)
    assert matrix[1][0] == pytest.approx(5.0)

    assert matrix[0][2] == pytest.approx(3.0)
    assert matrix[2][0] == pytest.approx(3.0)

    assert matrix[1][2] == pytest.approx(4.0)
    assert matrix[2][1] == pytest.approx(4.0)