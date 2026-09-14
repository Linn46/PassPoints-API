SUPPORTED_IMAGE_SIZES = frozenset({
	(800, 480),
	(1366, 768),
	(1920, 1080),
})


def is_supported_image_size(width: int, height: int) -> bool:
	return (width, height) in SUPPORTED_IMAGE_SIZES
