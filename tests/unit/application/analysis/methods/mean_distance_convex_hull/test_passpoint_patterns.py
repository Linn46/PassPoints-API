from app.application.analysis.methods.mean_distance_convex_hull.pattern_detector import (
    AGRUPADO,
    ALEATORIO,
    REGULAR,
    evaluate_password,
)


def test_mean_distance_detector_identifies_clustered_pattern():
    points = [
        (120, 120),
        (150, 130),
        (140, 150),
        (130, 160),
        (160, 180),
    ]

    result = evaluate_password(points, 1920, 1080, alpha=0.05)

    assert result.patrones == [AGRUPADO]
    assert result.aceptada is False


def test_mean_distance_detector_identifies_regular_pattern():
    points = [
        (100, 100),
        (100, 300),
        (100, 500),
        (300, 100),
        (300, 300),
        (300, 500),
        (500, 100),
        (500, 300),
        (500, 500),
        (700, 300),
    ]

    result = evaluate_password(points, 1920, 1080, alpha=0.05)

    assert result.patrones == [REGULAR]
    assert result.aceptada is False


def test_mean_distance_detector_identifies_linear_pattern():
    points = [
        (200, 540),
        (550, 540),
        (900, 540),
        (1250, 540),
        (1600, 540),
    ]

    result = evaluate_password(points, 1920, 1080, alpha=0.05)

    assert result.patrones == [REGULAR]
    assert result.aceptada is False


def test_mean_distance_detector_returns_consistent_evaluation():
    points = [
        (100, 100),
        (500, 100),
        (500, 500),
        (100, 500),
        (300, 300),
    ]

    result = evaluate_password(points, 1920, 1080, alpha=0.05)

    assert result.resultados
    assert isinstance(result.mensaje, str)
