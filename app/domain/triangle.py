from dataclasses import dataclass

from app.domain.point import Point


@dataclass(frozen=True, slots=True)
class Triangle:
    """
    Representa un triángulo formado por tres puntos.
    """

    vertices: tuple[Point, Point, Point]