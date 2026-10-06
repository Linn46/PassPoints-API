from app.domain.point import Point
from app.domain.triangulation import Triangulation
from app.geometry.delaunay.triangulator import triangulate


class TriangulationService:
    """Construye la triangulación de Delaunay del método A."""

    def execute(self, points: list[Point]) -> Triangulation:
        return triangulate(points)
