from dataclasses import dataclass

from app.domain.point import Point
from app.domain.security_assessment import SecurityAssessment
from app.domain.triangulation import Triangulation
from app.geometry.triangle.angles import (
    average_max_delaunay_angle,
)
from app.geometry.triangle.perimeter import (
    average_delaunay_perimeter,
)
from app.application.analysis.triangulation import (
    TriangulationService,
)
from app.application.analysis.security import assess_security
from app.statistics.angle_test.test import (
    AngleTestResult,
    run_test as run_angle_test,
)
from app.statistics.perimeter_test.test import (
    PerimeterTestStatistic,
    run_test as run_perimeter_test,
)


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """
    Resultado completo del análisis de una contraseña Passpoints.
    """

    triangulation: Triangulation
    average_perimeter: float
    average_max_angle: float
    perimeter_test: PerimeterTestStatistic
    angle_test: AngleTestResult
    security: SecurityAssessment


class AnalysisService:
    """
    Orquesta el análisis geométrico y estadístico.
    """

    def __init__(
        self,
        triangulation_service: TriangulationService | None = None,
    ) -> None:
        self._triangulation_service = (
            triangulation_service
            or TriangulationService()
        )

    def analyze(
        self,
        points: list[Point],
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
    ) -> AnalysisResult:

        triangulation = self._triangulation_service.execute(
            points
        )

        triangles = triangulation.triangles

        average_perimeter = (
            average_delaunay_perimeter(triangles)
        )

        average_max_angle = (
            average_max_delaunay_angle(triangles)
        )

        perimeter_test = run_perimeter_test(
            average_perimeter=average_perimeter,
            image_width=image_width,
            image_height=image_height,
            alpha=alpha,
        )

        angle_test = run_angle_test(
            average_max_angle=average_max_angle,
            alpha=alpha,
        )

        security = assess_security(
            perimeter_test=perimeter_test,
            angle_test=angle_test,
            points=points,
            triangles=triangles,
            image_width=image_width,
            image_height=image_height,
        )

        return AnalysisResult(
            triangulation=triangulation,
            average_perimeter=average_perimeter,
            average_max_angle=average_max_angle,
            perimeter_test=perimeter_test,
            angle_test=angle_test,
            security=security,
        )