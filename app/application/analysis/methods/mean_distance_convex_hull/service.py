from dataclasses import dataclass

from app.application.analysis.methods.delaunay_statistical.service import (
    AnalysisResult as DelaunayAnalysisResult,
    AnalysisService as DelaunayAnalysisService,
)
from app.domain.point import Point


@dataclass(frozen=True, slots=True)
class MeanDistanceConvexHullResult(DelaunayAnalysisResult):
    """Compatibility result for the mean-distance convex hull research line.

    The project keeps the Delaunay implementation as the concrete analysis engine
    while exposing the mean-distance method name through the public API surface.
    """

    method: str = "mean_distance_convex_hull"


class AnalysisService(DelaunayAnalysisService):
    """Thin compatibility wrapper for the newer method identifier."""

    def analyze(
        self,
        points: list[Point],
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
    ) -> MeanDistanceConvexHullResult:
        result = super().analyze(
            points=points,
            image_width=image_width,
            image_height=image_height,
            alpha=alpha,
        )
        return MeanDistanceConvexHullResult(
            triangulation=result.triangulation,
            average_perimeter=result.average_perimeter,
            average_max_angle=result.average_max_angle,
            perimeter_test=result.perimeter_test,
            angle_test=result.angle_test,
            security=result.security,
            method="mean_distance_convex_hull",
        )


__all__ = ["AnalysisService", "MeanDistanceConvexHullResult"]
