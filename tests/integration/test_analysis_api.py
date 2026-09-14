from fastapi.testclient import TestClient

from app.main import app


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

    assert "statistic" in data["perimeter_test"]
    assert "critical_value" in data["perimeter_test"]
    assert "reject_null" in data["perimeter_test"]

    assert "statistic" in data["angle_test"]
    assert "critical_value" in data["angle_test"]
    assert "reject_null" in data["angle_test"]


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