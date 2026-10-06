from app.application.analysis.methods.delaunay_statistical.service import (
    AnalysisService as DelaunayAnalysisService,
)

ANALYSIS_METHODS = {
    "delaunay_statistical": DelaunayAnalysisService,
}


class AnalysisMethodRegistry:
    """Registry for selecting an implemented analysis method."""

    @staticmethod
    def available_methods() -> tuple[str, ...]:
        return tuple(ANALYSIS_METHODS.keys())

    @staticmethod
    def get_service(method_name: str):
        service = ANALYSIS_METHODS.get(method_name)
        if service is None:
            raise ValueError(f"Unsupported analysis method: {method_name}")
        return service