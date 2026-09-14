from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NormalDistributionParameters:
    mean: float
    standard_deviation: float


AMADT_PARAMETERS = NormalDistributionParameters(
    mean=111.8,
    standard_deviation=17.2,
)