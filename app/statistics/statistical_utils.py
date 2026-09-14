def validate_alpha(alpha: float) -> None:
	if not 0 < alpha < 1:
		raise ValueError("Alpha must be between 0 and 1.")
