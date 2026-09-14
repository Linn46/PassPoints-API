from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JohnsonSBParameters:
    gamma: float
    delta: float
    lambda_: float
    xi: float


PARAMETERS_BY_IMAGE_SIZE = {
    (800, 480): JohnsonSBParameters(
        gamma=-0.44981,
        delta=2.7884,
        lambda_=2295.3,
        xi=-365.06,
    ),
    (1366, 768): JohnsonSBParameters(
        gamma=-0.25323,
        delta=1.9873,
        lambda_=2700.2,
        xi=8.2037,
    ),
    (1920, 1080): JohnsonSBParameters(
        gamma=-0.21458,
        delta=2.0283,
        lambda_=3940.5,
        xi=-30.961,
    ),
}