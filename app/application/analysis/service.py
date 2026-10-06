from app.application.analysis.registry import AnalysisMethodRegistry


class AnalysisService:
    """Servicio genérico que delega a la metodología seleccionada."""

    def __init__(self) -> None:
        self._registry = AnalysisMethodRegistry()

    def analyze(
        self,
        points,
        image_width: int,
        image_height: int,
        alpha: float = 0.05,
        method: str = "delaunay_statistical",
    ):
        service_class = self._registry.get_service(method)
        return service_class().analyze(
            points=points,
            image_width=image_width,
            image_height=image_height,
            alpha=alpha,
        )


__all__ = ["AnalysisService"]