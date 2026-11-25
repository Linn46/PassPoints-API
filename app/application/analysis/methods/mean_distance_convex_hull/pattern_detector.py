from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from math import hypot

from app.application.analysis.methods.mean_distance_convex_hull.convex_hull import (
    hull_area, hull_perimeter,
)
from app.statistics.mean_distance_convex_hull.tests import run_aec, run_dm, run_pec

AGRUPADO = "agrupado"
REGULAR = "regular"
NO_DETECTADO = "sin_patron_detectado"


@dataclass(frozen=True, slots=True)
class ResultadoPrueba:
    test: str
    patron: str
    estadigrafo: float
    rechazo_h0: bool


@dataclass(frozen=True, slots=True)
class Evaluacion:
    patrones: list[str]
    aceptada: bool
    mensaje: str
    resultados: dict[str, ResultadoPrueba] = field(default_factory=dict)


def mean_distance(points: list[tuple[float, float]]) -> float:
    pairs = [hypot(a[0] - b[0], a[1] - b[1]) for a, b in combinations(points, 2)]
    return sum(pairs) / len(pairs) if pairs else 0.0


def evaluate_password(
    points: list[tuple[float, float]], image_width: int, image_height: int,
    alpha: float = 0.05,
) -> Evaluacion:
    if len(points) != 5:
        raise ValueError("Los contrastes DM/PEC/AEC requieren exactamente cinco puntos.")
    if len(set(points)) != 5:
        raise ValueError("Los cinco puntos deben ser distintos.")

    dm = run_dm(mean_distance(points), image_width, image_height, alpha)
    patterns: list[str] = []
    if dm.detected_pattern:
        patterns.append(dm.detected_pattern)

    results = {"DM": ResultadoPrueba("DM", dm.detected_pattern or NO_DETECTADO, dm.statistic, dm.reject_null)}
    # PEC y AEC solo tienen parámetros publicados para 1920x1080.
    if (image_width, image_height) == (1920, 1080):
        # El dominio Johnson SB es estricto. Una observación fuera de él no
        # es clasificable con PEC; se omite ese test en vez de provocar HTTP 500.
        try:
            pec = run_pec(hull_perimeter(points), image_width, image_height, alpha)
        except ValueError as exc:
            if "dominio" not in str(exc):
                raise
        else:
            if pec.detected_pattern == AGRUPADO and AGRUPADO not in patterns:
                patterns.append(AGRUPADO)
            results["PEC"] = ResultadoPrueba("PEC", pec.detected_pattern or NO_DETECTADO, pec.statistic, pec.reject_null)
        aec = run_aec(hull_area(points), image_width, image_height, alpha)
        if aec.detected_pattern == REGULAR and REGULAR not in patterns:
            patterns.append(REGULAR)
        results["AEC"] = ResultadoPrueba("AEC", aec.detected_pattern or NO_DETECTADO, aec.statistic, aec.reject_null)

    accepted = not patterns
    unclassified_rejections = [
        name for name, result in results.items()
        if result.rechazo_h0 and result.patron == NO_DETECTADO
    ]
    if patterns:
        message = (
            "Se detectaron indicios estadísticos compatibles con: "
            + ", ".join(patterns) + "."
        )
    else:
        message = (
            "No se identificó un patrón agrupado o regular en las regiones críticas "
            "cuya capacidad de detección fue respaldada experimentalmente. "
            "Esta versión no clasifica patrones lineales (Line) mediante DM/PEC/AEC. "
            "La ausencia de detección no demuestra que la selección sea aleatoria."
        )
    if unclassified_rejections:
        message += (
            " Se rechazó H0 en una región sin clasificación respaldada "
            "experimentalmente para: " + ", ".join(unclassified_rejections) + "."
        )
    return Evaluacion(patterns, accepted, message, results)
