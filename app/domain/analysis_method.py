from enum import Enum


class AnalysisMethod(str, Enum):
    """Names of analysis methodologies implemented by the system."""

    DELAUNAY_STATISTICAL = "delaunay_statistical"