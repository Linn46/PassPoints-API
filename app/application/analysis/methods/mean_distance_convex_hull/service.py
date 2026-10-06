from dataclasses import dataclass
from typing import Sequence

from app.application.analysis.methods.mean_distance_convex_hull.pattern_detector import (
    AGRUPADO,
    ALEATORIO,
    REGULAR,
    Evaluacion,
    evaluate_password,
)
from app.domain.point import Point
from app.domain.security_assessment import SecurityAssessment


@dataclass(frozen=True, slots=True)
class MeanDistanceConvexHullResult:
    """Resultado del análisis de la metodología de distancia media + convex hull."""

    evaluation: Evaluacion
    security: SecurityAssessment
    method: str = "mean_distance_convex_hull"


AnalysisResult = MeanDistanceConvexHullResult


def _pattern_label(raw: str) -> str:
    mapping = {
        AGRUPADO: "Patrón agrupado",
        REGULAR: "Patrón regular",
        ALEATORIO: "Aleatorio",
    }
    return mapping.get(raw, raw)


def _security_assessment_from_evaluation(evaluation: Evaluacion) -> SecurityAssessment:
    if not evaluation.patrones:
        return SecurityAssessment(
            is_weak=False,
            level="Alta",
            patterns=[],
            title="Contraseña sin patrón débil detectado",
            explanation=(
                "No se detectó un patrón geométrico no aleatorio con los "
                "criterios utilizados por el análisis."
            ),
        )

    pattern_names = [_pattern_label(pattern) for pattern in evaluation.patrones]
    pattern_text = ", ".join(pattern_names)
    evidence: list[str] = []

    for result in evaluation.resultados.values():
        if result.patron == ALEATORIO:
            continue
        if result.test == "DM":
            evidence.append(f"el test DM indicó {result.patron} (Z={result.estadigrafo:.2f})")
        elif result.test == "PEC":
            evidence.append(f"el test PEC indicó agrupamiento (Z={result.estadigrafo:.2f})")
        elif result.test == "AEC":
            evidence.append(f"el test AEC indicó regularidad (área={result.estadigrafo:.2f})")

    if not evidence:
        evidence.append("el análisis estadístico rechazó la aleatoriedad")

    level = "Baja" if len(pattern_names) > 1 or "Patrón agrupado" in pattern_names else "Media"

    return SecurityAssessment(
        is_weak=True,
        level=level,
        patterns=pattern_names,
        title="Contraseña no segura",
        explanation=(
            "Los puntos seleccionados presentan características compatibles "
            f"con {pattern_text}. La decisión se basa en que "
            f"{' y '.join(evidence)}."
        ),
    )


class AnalysisService:
    """Orquesta la metodología específica de distancia media + convex hull."""

    def analyze(
        self,
        points: Sequence[Point | tuple[float, float]],
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
    ) -> MeanDistanceConvexHullResult:
        normalized = [
            (float(point.x), float(point.y)) if isinstance(point, Point) else (float(point[0]), float(point[1]))
            for point in points
        ]
        evaluation = evaluate_password(normalized, image_width, image_height, alpha)
        return MeanDistanceConvexHullResult(
            evaluation=evaluation,
            security=_security_assessment_from_evaluation(evaluation),
            method="mean_distance_convex_hull",
        )
