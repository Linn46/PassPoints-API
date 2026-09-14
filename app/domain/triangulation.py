from dataclasses import dataclass

from app.domain.triangle import Triangle


@dataclass(frozen=True, slots=True)
class Triangulation:
    """
    Representa el resultado de una triangulación.
    """

    triangles: tuple[Triangle, ...]
