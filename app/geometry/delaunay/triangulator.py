import numpy as np
from scipy.spatial import Delaunay as SciPyDelaunay
from scipy.spatial import QhullError

from app.domain.point import Point
from app.domain.triangle import Triangle
from app.domain.triangulation import Triangulation
from app.geometry.delaunay.validator import (
    DelaunayValidationError,
    validate_points,
)


def triangulate(points: list[Point]) -> Triangulation:
    """
    Construye la triangulación de Delaunay de los cinco puntos.
    """

    validate_points(points)

    coordinates = np.asarray(
        [(point.x, point.y) for point in points],
        dtype=float,
    )

    try:
        delaunay = SciPyDelaunay(coordinates)
    except QhullError as exc:
        raise DelaunayValidationError(
            "The points do not admit a valid Delaunay triangulation."
        ) from exc

    triangles = tuple(
        Triangle(
            tuple(
                points[int(index)]
                for index in simplex
            )
        )
        for simplex in delaunay.simplices
    )

    return Triangulation(
        triangles=triangles,
    )