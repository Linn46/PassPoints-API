from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TestResult:
    """
    Resultado de una prueba estadística.
    """

    statistic: float
    critical_value: float
    reject_null: bool
    alpha: float


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """
    Resultado completo del análisis de una contraseña Passpoints.
    """

    average_perimeter: float
    average_max_angle: float
    perimeter_test: TestResult | None
    angle_test: TestResult | None
    method: str = "delaunay_statistical"