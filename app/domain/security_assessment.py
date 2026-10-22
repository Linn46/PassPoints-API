from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PatternDetail:
    pattern_id: str
    methods: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SecurityAssessment:
    """Interpretación cualitativa de los tests estadísticos."""

    is_weak: bool
    level: str
    patterns: list[str]
    title: str
    explanation: str
    pattern_details: list[PatternDetail] = field(default_factory=list)