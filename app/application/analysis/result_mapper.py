from app.application.analysis.methods.delaunay_statistical.service import AnalysisResult
from app.domain.analysis_result import AnalysisResult as DomainAnalysisResult


def to_domain_result(result: AnalysisResult) -> DomainAnalysisResult:
    """Convierte el resultado del servicio a un modelo de dominio compacto."""
    return DomainAnalysisResult(
        average_perimeter=result.average_perimeter,
        average_max_angle=result.average_max_angle,
        perimeter_test=result.perimeter_test,
        angle_test=result.angle_test,
        method=result.method,
    )
