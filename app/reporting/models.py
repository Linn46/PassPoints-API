from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TestReport:
    name: str
    description: str
    statistic: float
    critical_value: float
    alpha: float
    reject_null: bool

    @property
    def decision(self) -> str:
        if self.reject_null:
            return "REJECT H0"

        return "DO NOT REJECT H0"