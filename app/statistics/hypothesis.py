def reject_null_right_tail(statistic: float, critical_value: float) -> bool:
	"""Decide una prueba unilateral derecha."""
	return statistic > critical_value


def reject_null_two_tailed(statistic: float, critical_value: float) -> bool:
	"""Decide una prueba bilateral usando un valor crítico positivo."""
	return statistic < -critical_value or statistic > critical_value
