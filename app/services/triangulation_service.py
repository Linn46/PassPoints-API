from app.domain.point import Point
from app.domain.triangulation import Triangulation
from app.geometry.delaunay.triangulator import triangulate


class TriangulationService:
    """
    Servicio encargado de construir la triangulación de Delaunay
    a partir de los puntos de una contraseña Passpoints.
    """

    def execute(
        self,
        points: list[Point],
    ) -> Triangulation:
        """
        Construye y devuelve la triangulación de Delaunay.
        """

        return triangulate(points)