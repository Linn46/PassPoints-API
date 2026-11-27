"""Contrastes de Herrera para cinco puntos PassPoint.

Los parámetros PEC y AEC publicados están calibrados únicamente para 1920x1080.
Se usan únicamente las colas cuya capacidad de detección se reporta como efectiva
por la tesis: PEC cola izquierda (agrupamiento), AEC cola derecha (regularidad).
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from statistics import NormalDist


@dataclass(frozen=True, slots=True)
class TestResult:
    name: str
    statistic: float
    critical_lower: float
    critical_upper: float
    reject_null: bool
    detected_pattern: str | None
    alpha: float


DM_PARAMETERS = {
    (800, 480): (339.0, 71.0),
    (1366, 768): (568.0, 120.0),
    (1920, 1080): (798.0, 168.0),
}
PEC_PARAMETERS_1920 = (-0.65612, 1.5922, 4575.1, 495.15)
AEC_WEIBULL_1920 = (2.2478, 500760.0)  # forma a, escala b


def _validate_alpha(alpha: float) -> None:
    if not isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha debe estar entre 0 y 1 (excluidos).")


def _two_tail_bounds(alpha: float) -> tuple[float, float]:
    _validate_alpha(alpha)
    z = NormalDist().inv_cdf(1 - alpha / 2)
    return -z, z


def run_dm(value: float, width: int, height: int, alpha: float = 0.05) -> TestResult:
    _validate_alpha(alpha)
    if not isfinite(value):
        raise ValueError("DM debe ser finita.")
    try:
        mu, sigma = DM_PARAMETERS[(width, height)]
    except KeyError as exc:
        raise ValueError(f"Resolución no calibrada para DM: {width}x{height}.") from exc
    z = (value - mu) / sigma
    lo, hi = _two_tail_bounds(alpha)
    pattern = "agrupado" if z < lo else "regular" if z > hi else None
    return TestResult("DM", z, lo, hi, pattern is not None, pattern, alpha)


def run_pec(value: float, width: int, height: int, alpha: float = 0.05) -> TestResult:
    _validate_alpha(alpha)
    if (width, height) != (1920, 1080):
        raise ValueError("PEC solo está calibrado para imágenes de 1920x1080.")
    if not isfinite(value):
        raise ValueError("PEC debe ser finito.")
    gamma, delta, scale, xi = PEC_PARAMETERS_1920
    numerator = value - xi
    denominator = scale + xi - value
    if numerator <= 0 or denominator <= 0:
        raise ValueError("PEC fuera del dominio de la transformación Johnson SB.")
    z = gamma + delta * log(numerator / denominator)
    lo, hi = _two_tail_bounds(alpha)
    # La tesis reporta detección efectiva de agrupamiento en la cola izquierda.
    pattern = "agrupado" if z < lo else None
    return TestResult("PEC", z, lo, hi, z < lo or z > hi, pattern, alpha)


def _weibull_quantile(probability: float, shape: float, scale: float) -> float:
    return scale * (-log(1 - probability)) ** (1 / shape)


def run_aec(value: float, width: int, height: int, alpha: float = 0.05) -> TestResult:
    _validate_alpha(alpha)
    if (width, height) != (1920, 1080):
        raise ValueError("AEC solo está calibrado para imágenes de 1920x1080.")
    if not isfinite(value) or value < 0:
        raise ValueError("AEC debe ser finita y no negativa.")
    shape, scale = AEC_WEIBULL_1920
    lo = _weibull_quantile(alpha / 2, shape, scale)
    hi = _weibull_quantile(1 - alpha / 2, shape, scale)
    # La tesis reporta detección efectiva de regularidad en la cola derecha.
    pattern = "regular" if value > hi else None
    return TestResult("AEC", value, lo, hi, value < lo or value > hi, pattern, alpha)
