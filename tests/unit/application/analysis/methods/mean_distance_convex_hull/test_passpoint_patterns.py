import pytest

from app.application.analysis.methods.mean_distance_convex_hull.pattern_detector import (
    AGRUPADO, REGULAR, evaluate_password,
)
from app.statistics.mean_distance_convex_hull.tests import run_aec, run_dm, run_pec


def test_dm_uses_normal_reference_and_detects_lower_tail():
    result = run_dm(399.0, 1920, 1080, alpha=0.1)
    assert result.statistic == pytest.approx((399 - 798) / 168)
    assert result.detected_pattern == AGRUPADO


def test_dm_rejects_unsupported_resolution():
    with pytest.raises(ValueError, match="no calibrada"):
        run_dm(500, 900, 600)


def test_pec_requires_calibrated_resolution():
    with pytest.raises(ValueError, match="1920x1080"):
        run_pec(1000, 1366, 768)


def test_pec_rejects_values_outside_johnson_domain():
    with pytest.raises(ValueError, match="dominio"):
        run_pec(5071, 1920, 1080)


def test_aec_uses_weibull_percentile_region():
    # Área cercana al máximo del rectángulo: cola derecha de la Weibull.
    result = run_aec(1_000_000, 1920, 1080, alpha=0.05)
    assert result.detected_pattern == REGULAR


def test_evaluation_requires_exactly_five_distinct_points():
    with pytest.raises(ValueError, match="exactamente cinco"):
        evaluate_password([(0, 0), (1, 1)], 1920, 1080)
    with pytest.raises(ValueError, match="distintos"):
        evaluate_password([(0, 0)] * 5, 1920, 1080)


def test_evaluation_reports_only_supported_tests_for_800x480():
    points = [(100, 100), (300, 100), (500, 300), (200, 400), (700, 450)]
    result = evaluate_password(points, 800, 480)
    assert set(result.resultados) == {"DM"}


def test_evaluation_reports_three_tests_for_1920x1080():
    points = [(100, 100), (300, 100), (500, 300), (200, 400), (700, 450)]
    result = evaluate_password(points, 1920, 1080)
    assert set(result.resultados) == {"DM", "PEC", "AEC"}


def test_aec_lower_tail_is_rejected_but_not_labeled_as_validated_cluster():
    result = run_aec(1_000.0, 1920, 1080, alpha=0.05)
    assert result.reject_null is True
    assert result.detected_pattern is None


def test_unvalidated_tail_rejection_is_reported_without_claiming_randomness():
    # Cinco puntos muy próximos generan un AEC en la cola inferior.
    points = [(100, 100), (101, 100), (101, 101), (100, 101), (100.5, 100.5)]
    result = evaluate_password(points, 1920, 1080, alpha=0.05)
    assert "AEC" in result.resultados
    assert result.resultados["AEC"].rechazo_h0 is True
    assert result.resultados["AEC"].patron == "sin_patron_detectado"
    assert "rechazó H0" in result.mensaje
    assert "sin clasificación respaldada" in result.mensaje
