from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    """Interpretación cualitativa de los tests estadísticos."""

    is_weak: bool
    level: str
    patterns: list[str]
    title: str
    explanation: str