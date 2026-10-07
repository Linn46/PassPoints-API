from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

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


def _relative_gap(actual: float, reference: float) -> float:
    if reference <= 0:
        return 0.0
    return (actual - reference) / reference


def _distance_cv(points: list[tuple[float, float]]) -> float:
    if len(points) < 2:
        return 1.0

    distances: list[float] = []
    for index, point in enumerate(points):
        for other in points[index + 1 :]:
            distances.append(sqrt((point[0] - other[0]) ** 2 + (point[1] - other[1]) ** 2))

    if len(distances) < 2:
        return 1.0

    mean_value = sum(distances) / len(distances)
    if mean_value <= 0:
        return 1.0

    variance = sum((distance - mean_value) ** 2 for distance in distances) / len(distances)
    return sqrt(variance) / mean_value


def _cluster_strength(points: list[tuple[float, float]], image_width: float, image_height: float) -> float:
    if not points:
        return 0.0

    expected = mean_distance_rectangle(image_width, image_height)
    actual = mean_distance(points)
    if expected <= 0:
        return 0.0

    mean_component = max(0.0, 1.0 - (actual / expected))
    perimeter = hull_perimeter(points)
    expected_perimeter = 2.0 * (image_width + image_height)
    perimeter_component = max(0.0, 1.0 - (perimeter / max(expected_perimeter, 1.0)))
    return max(0.0, (mean_component + perimeter_component) / 2.0)


def _regularity_score(points: list[tuple[float, float]], image_width: float, image_height: float) -> float:
    if not points:
        return 0.0

    distances_cv = _distance_cv(points)
    regularity_component = max(0.0, 1.0 - min(distances_cv, 1.0))

    image_area = max(image_width * image_height, 1.0)
    area_ratio = hull_area(points) / image_area
    spread_component = max(0.0, area_ratio)

    return max(0.0, (regularity_component * 0.7) + (spread_component * 0.3))


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
    area_ratio = hull_area(points) / max(image_width * image_height, 1.0)
    pattern = ALEATORIO

    if cluster_score >= 0.55 and area_ratio < 0.08:
        pattern = AGRUPADO
    elif area_ratio >= 0.08 and regularity >= 0.40:
        pattern = REGULAR
    elif cluster_score >= 0.45:
        pattern = AGRUPADO
    elif regularity >= 0.45:
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

    expected_mean = mean_distance_rectangle(image_width, image_height)
    expected_perimeter = 2.0 * (image_width + image_height)
    expected_area = max(image_width * image_height, 1.0)

    dm_stat = _relative_gap(mean_distance(points), expected_mean)
    pec_stat = _relative_gap(hull_perimeter(points), expected_perimeter)
    aec_stat = _relative_gap(hull_area(points), expected_area)

    resultados = {
        "DM": ResultadoPrueba("DM", pattern, dm_stat),
        "PEC": ResultadoPrueba(
            "PEC",
            AGRUPADO if pattern == AGRUPADO else REGULAR,
            pec_stat,
        ),
        "AEC": ResultadoPrueba(
            "AEC",
            REGULAR if pattern == REGULAR else AGRUPADO,
            aec_stat,
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
