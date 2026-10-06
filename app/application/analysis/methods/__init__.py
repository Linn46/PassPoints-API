"""Method-specific implementations for each research line."""

from app.application.analysis.methods.delaunay_statistical.service import (
    AnalysisResult as DelaunayAnalysisResult,
    AnalysisService as DelaunayAnalysisService,
)

__all__ = [
    "DelaunayAnalysisResult",
    "DelaunayAnalysisService",
]
