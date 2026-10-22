from dataclasses import dataclass

from app.application.analysis.methods.mean_distance_convex_hull.pattern_detector import (
    AGRUPADO,
    LINEAR,
    REGULAR,
    evaluate_password,
)
from app.domain.point import Point
from app.domain.security_assessment import PatternDetail, SecurityAssessment


@dataclass(frozen=True, slots=True)
class MeanDistanceConvexHullResult:
    security: SecurityAssessment
    method: str = "mean_distance_convex_hull"


class AnalysisService:
    """Analyze point distribution with pairwise distances and convex-hull metrics."""

    def analyze(
        self,
        points: list[Point],
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
    ) -> MeanDistanceConvexHullResult:
        evaluation = evaluate_password(
            [(point.x, point.y) for point in points],
            image_width,
            image_height,
            alpha,
        )
        pattern_details = [
            PatternDetail(
                pattern_id={
                    AGRUPADO: "clustered",
                    REGULAR: "regular",
                    LINEAR: "linear",
                }[pattern],
                methods=("mean_distance_convex_hull",),
            )
            for pattern in evaluation.patrones
        ]
        is_weak = not evaluation.aceptada
        security = SecurityAssessment(
            is_weak=is_weak,
            level=(
                "Baja"
                if is_weak and (AGRUPADO in evaluation.patrones or len(evaluation.patrones) > 1)
                else "Media"
                if is_weak
                else "Alta"
            ),
            patterns=[
                {
                    AGRUPADO: "Patrón agrupado",
                    REGULAR: "Patrón regular",
                    LINEAR: "Patrón Line",
                }[pattern]
                for pattern in evaluation.patrones
            ],
            title="Contraseña no segura" if is_weak else "Contraseña sin patrón débil detectado",
            explanation=evaluation.mensaje,
            pattern_details=pattern_details,
        )
        return MeanDistanceConvexHullResult(
            security=security,
            method="mean_distance_convex_hull",
        )


__all__ = ["AnalysisService", "MeanDistanceConvexHullResult"]
