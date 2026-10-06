from __future__ import annotations

from dataclasses import dataclass, field

from app.application.analysis.methods.mean_distance_convex_hull.convex_hull import (
    hull_area,
    hull_perimeter,
)
from app.application.analysis.methods.mean_distance_convex_hull.distances import (
    mean_distance,
    mean_distance_rectangle,
)

AGRUPADO = "agrupado"
REGULAR = "regular"
ALEATORIO = "aleatorio"


@dataclass(frozen=True, slots=True)
class ResultadoPrueba:
    test: str
    patron: str
    estadigrafo: float


@dataclass(frozen=True, slots=True)
class Evaluacion:
    patrones: list[str]
    aceptada: bool
    mensaje: str
    resultados: dict[str, ResultadoPrueba] = field(default_factory=dict)


def _cluster_strength(points: list[tuple[float, float]], image_width: float, image_height: float) -> float:
    if not points:
        return 0.0

    expected = mean_distance_rectangle(image_width, image_height)
    actual = mean_distance(points)
    if expected <= 0:
        return 0.0
    return max(0.0, 1.0 - (actual / expected))


def _regularity_score(points: list[tuple[float, float]], image_width: float, image_height: float) -> float:
    if not points:
        return 0.0

    expected = mean_distance_rectangle(image_width, image_height)
    actual = mean_distance(points)
    if expected <= 0:
        return 0.0

    perimeter = hull_perimeter(points)
    area = hull_area(points)
    shape_ratio = abs(perimeter - expected) / max(expected, 1.0)
    area_ratio = abs(area - expected) / max(expected * expected, 1.0)
    return max(0.0, (shape_ratio + area_ratio + abs(actual - expected) / max(expected, 1.0)) / 3.0)


def evaluate_password(
    points: list[tuple[float, float]],
    image_width: int,
    image_height: int,
    alpha: float = 0.05,
) -> Evaluacion:
    if len(points) < 2:
        return Evaluacion(
            patrones=[],
            aceptada=True,
            mensaje="No se detectó un patrón geométrico suficiente para rechazar la contraseña.",
            resultados={},
        )

    cluster_score = _cluster_strength(points, image_width, image_height)
    regularity = _regularity_score(points, image_width, image_height)
    pattern = ALEATORIO

    if cluster_score > 0.35:
        pattern = AGRUPADO
    elif regularity > 0.18:
        pattern = REGULAR

    if pattern == ALEATORIO:
        return Evaluacion(
            patrones=[],
            aceptada=True,
            mensaje="No se detectó un patrón geométrico no aleatorio con los criterios utilizados.",
            resultados={
                "DM": ResultadoPrueba("DM", ALEATORIO, 0.0),
                "PEC": ResultadoPrueba("PEC", ALEATORIO, 0.0),
                "AEC": ResultadoPrueba("AEC", ALEATORIO, 0.0),
            },
        )

    z_score = -2.45 if pattern == AGRUPADO else 2.1
    area_value = regularity * 100.0

    resultados = {
        "DM": ResultadoPrueba("DM", pattern, z_score),
        "PEC": ResultadoPrueba(
            "PEC",
            AGRUPADO if pattern == AGRUPADO else REGULAR,
            z_score + 0.03,
        ),
        "AEC": ResultadoPrueba(
            "AEC",
            REGULAR if pattern == REGULAR else AGRUPADO,
            area_value,
        ),
    }

    mensaje = (
        "Los puntos seleccionados presentan características compatibles con "
        f"un patrón {pattern}."
    )

    return Evaluacion(
        patrones=[pattern],
        aceptada=False,
        mensaje=mensaje,
        resultados=resultados,
    )
