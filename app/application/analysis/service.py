from app.application.analysis.methods.delaunay_statistical.service import AnalysisResult
from app.application.analysis.methods.mean_distance_convex_hull.service import (
    MeanDistanceConvexHullResult,
)
from app.application.analysis.registry import AnalysisMethodRegistry
from app.domain.point import Point


class AnalysisService:
    """Fachada que delega en el método seleccionado."""

    def __init__(self) -> None:
        self._registry = AnalysisMethodRegistry()

    def analyze(
        self,
        points: list[Point],
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
        method: str = "delaunay_statistical",
    ) -> AnalysisResult | MeanDistanceConvexHullResult:
        service_class = self._registry.get_service(method)
        return service_class().analyze(
            points=points,
            image_width=image_width,
            image_height=image_height,
            alpha=alpha,
        )


__all__ = ["AnalysisService"]
