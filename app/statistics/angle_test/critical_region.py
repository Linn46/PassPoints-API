from statistics import NormalDist


def critical_value(alpha: float) -> float:
    """
    Calcula el valor crítico z_alpha para un test unilateral
    de cola derecha basado en la distribución normal estándar.
    """

    if not 0 < alpha < 1:
        raise ValueError("Alpha must be between 0 and 1.")

    return NormalDist().inv_cdf(1 - alpha)


def is_in_critical_region(
    statistic: float,
    alpha: float,
) -> bool:
    """
    Determina si el estadístico pertenece a la región crítica.

    Para este test:

        RC = {Z : Z > z_alpha}
    """

    return statistic > critical_value(alpha)