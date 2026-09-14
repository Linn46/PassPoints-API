from statistics import NormalDist


def critical_value(alpha: float) -> float:
    """
    Obtiene z_(alpha/2) para un test bilateral basado
    en la distribución normal estándar.
    """
    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    return NormalDist().inv_cdf(1 - alpha / 2)


def is_in_critical_region(
    statistic: float,
    alpha: float,
) -> bool:
    """
    Determina si el estadístico pertenece a la región crítica
    del test bilateral.

    RC = {z : Z < -z_(alpha/2) or Z > z_(alpha/2)}
    """
    critical = critical_value(alpha)

    return (
        statistic < -critical
        or statistic > critical
    )