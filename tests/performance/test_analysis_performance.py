from time import perf_counter

from app.domain.point import Point
from app.application.analysis.service import AnalysisService


def test_repeated_analysis_completes_in_reasonable_time():
	points = [
		Point(100, 100),
		Point(500, 100),
		Point(500, 500),
		Point(100, 500),
		Point(300, 300),
	]
	service = AnalysisService()

	started = perf_counter()
	results = [
		service.analyze(points, 1920, 1080)
		for _ in range(100)
	]
	elapsed = perf_counter() - started

	assert len(results) == 100
	assert all(result.average_perimeter > 0 for result in results)
	assert elapsed < 5.0
