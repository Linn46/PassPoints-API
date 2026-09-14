from app.domain.analysis_result import AnalysisResult as DomainAnalysisResult
from app.services.analysis_service import AnalysisResult


def to_domain_result(result: AnalysisResult) -> DomainAnalysisResult:
	"""Convierte el resultado del servicio a un modelo de dominio compacto."""
	return DomainAnalysisResult(
		average_perimeter=result.average_perimeter,
		average_max_angle=result.average_max_angle,
		perimeter_test=result.perimeter_test,
		angle_test=result.angle_test,
	)
