from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.statistics.angle_test.test import run_test as run_angle_test
from app.statistics.perimeter_test.test import (
    run_test as run_perimeter_test,
)


client = TestClient(app)


def valid_request() -> dict:
    return {
        "points": [
            {"x": 100, "y": 100},
            {"x": 500, "y": 100},
            {"x": 500, "y": 500},
            {"x": 100, "y": 500},
            {"x": 300, "y": 300},
        ],
        "image_width": 1920,
        "image_height": 1080,
        "alpha": 0.05,
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analysis_endpoint_returns_complete_result():
    response = client.post(
        "/api/v1/analysis",
        json=valid_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["points"]) == 5
    assert len(data["triangles"]) > 0

    assert data["average_perimeter"] > 0
    assert 0 < data["average_max_angle"] < 180

    expected_perimeter = run_perimeter_test(
        average_perimeter=data["average_perimeter"],
        image_width=1920,
        image_height=1080,
        alpha=0.05,
    )
    expected_angle = run_angle_test(
        average_max_angle=data["average_max_angle"],
        alpha=0.05,
    )

    assert data["perimeter_test"]["statistic"] == pytest.approx(
        expected_perimeter.statistic
    )
    assert data["perimeter_test"]["critical_value"] == pytest.approx(
        expected_perimeter.critical_value
    )
    assert data["perimeter_test"]["alpha"] == pytest.approx(
        expected_perimeter.alpha
    )
    assert data["perimeter_test"]["reject_null"] is expected_perimeter.reject_null

    assert data["angle_test"]["statistic"] == pytest.approx(
        expected_angle.statistic
    )
    assert data["angle_test"]["critical_value"] == pytest.approx(
        expected_angle.critical_value
    )
    assert data["angle_test"]["alpha"] == pytest.approx(
        expected_angle.alpha
    )
    assert data["angle_test"]["reject_null"] is expected_angle.reject_null

    assert "statistic" in data["perimeter_test"]
    assert "critical_value" in data["perimeter_test"]
    assert "reject_null" in data["perimeter_test"]

    assert "statistic" in data["angle_test"]
    assert "critical_value" in data["angle_test"]
    assert "reject_null" in data["angle_test"]

    assert set(data["security"]) == {
        "is_weak",
        "level",
        "patterns",
        "title",
        "explanation",
    }
    assert isinstance(data["security"]["is_weak"], bool)
    assert data["security"]["level"] in {"Alta", "Media", "Baja"}


def test_analysis_endpoint_exposes_no_rejection_for_reference_random_case():
    request = valid_request()
    request["points"] = [
        {"x": 214, "y": 173},
        {"x": 843, "y": 921},
        {"x": 1472, "y": 284},
        {"x": 1165, "y": 735},
        {"x": 521, "y": 492},
    ]

    response = client.post("/api/v1/analysis", json=request)

    assert response.status_code == 200
    result = response.json()

    assert result["perimeter_test"]["reject_null"] is False
    assert result["angle_test"]["reject_null"] is False
    assert result["security"]["is_weak"] is False
    assert result["security"]["patterns"] == []


def test_analysis_endpoint_rejects_less_than_five_points():
    request = valid_request()
    request["points"] = request["points"][:4]

    response = client.post(
        "/api/v1/analysis",
        json=request,
    )

    assert response.status_code == 422


def test_analysis_endpoint_rejects_point_outside_image():
    request = valid_request()
    request["points"][0] = {
        "x": 2000,
        "y": 100,
    }

    response = client.post(
        "/api/v1/analysis",
        json=request,
    )

    assert response.status_code == 422


def test_analysis_endpoint_rejects_invalid_alpha():
    request = valid_request()
    request["alpha"] = 1.5

    response = client.post(
        "/api/v1/analysis",
        json=request,
    )

    assert response.status_code == 422