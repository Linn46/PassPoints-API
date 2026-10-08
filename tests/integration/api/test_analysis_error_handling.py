import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAnalysisErrorHandling:
    """Test error handling in the analysis API."""

    def test_duplicate_points_returns_422_with_error_details(self, client):
        """Test that duplicate points returns a 422 error with error details."""
        request_data = {
            "points": [
                {"x": 100, "y": 100},
                {"x": 100, "y": 100},  # Duplicate
                {"x": 500, "y": 100},
                {"x": 500, "y": 500},
                {"x": 100, "y": 500},
            ],
            "image_width": 1920,
            "image_height": 1080,
            "alpha": 0.05,
            "method": "delaunay_statistical",
        }

        response = client.post("/api/v1/analysis", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "Request Validation Error"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "body"
        assert "Duplicate points found at indices" in data["errors"][0]["message"]
        assert "input" not in data

    def test_insufficient_points_returns_422(self, client):
        """Test that insufficient points returns a 422 error."""
        request_data = {
            "points": [
                {"x": 100, "y": 100},
                {"x": 500, "y": 100},
                {"x": 500, "y": 500},
                {"x": 100, "y": 500},
            ],
            "image_width": 1920,
            "image_height": 1080,
            "alpha": 0.05,
            "method": "delaunay_statistical",
        }

        response = client.post("/api/v1/analysis", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "Request Validation Error"
        assert len(data["errors"]) == 1

    def test_points_outside_image_bounds_return_422(self, client):
        """Test that points outside image bounds return a 422 error."""
        request_data = {
            "points": [
                {"x": 100, "y": 100},
                {"x": 5000, "y": 100},  # Outside image width
                {"x": 500, "y": 500},
                {"x": 100, "y": 500},
                {"x": 300, "y": 300},
            ],
            "image_width": 1920,
            "image_height": 1080,
            "alpha": 0.05,
            "method": "delaunay_statistical",
        }

        response = client.post("/api/v1/analysis", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "Request Validation Error"
        assert len(data["errors"]) == 1
        assert "outside the image" in data["errors"][0]["message"]

    def test_valid_request_succeeds(self, client):
        """Test that a valid request succeeds."""
        request_data = {
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
            "method": "delaunay_statistical",
        }

        response = client.post("/api/v1/analysis", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "points" in data
        assert len(data["points"]) == 5
        assert "security" in data

    def test_collinear_points_return_400_with_detailed_error(self, client):
        """Test that collinear points return a 400 error with detailed validation info."""
        request_data = {
            "points": [
                {"x": 0, "y": 0},
                {"x": 100, "y": 100},
                {"x": 200, "y": 200},
                {"x": 300, "y": 300},
                {"x": 400, "y": 400},
            ],
            "image_width": 1920,
            "image_height": 1080,
            "alpha": 0.05,
            "method": "delaunay_statistical",
        }

        response = client.post("/api/v1/analysis", json=request_data)

        # Collinear points will be caught by the business logic
        # and return a 400 error via the custom exception handler
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "Validation Error" in data.get("error", "")
        assert "type" in data
        assert data["type"] == "collinear_points"
