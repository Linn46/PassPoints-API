from app.domain.point import Point
from app.application.analysis.service import AnalysisService


def test_analysis_service_supports_all_configured_image_sizes():
	points = [
		Point(100, 100),
		Point(500, 100),
		Point(500, 500),
		Point(100, 500),
		Point(300, 300),
	]

	for width, height in ((800, 480), (1366, 768), (1920, 1080)):
		result = AnalysisService().analyze(points, width, height)

		assert result.perimeter_test.alpha == 0.05
		assert result.average_perimeter > 0
