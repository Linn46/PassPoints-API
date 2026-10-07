import pytest

from app.domain.point import Point
from app.geometry.delaunay.validator import (
    DelaunayValidationError,
    validate_points,
)


class TestDelaunayValidationEnhanced:
    """Test enhanced error handling for Delaunay validation."""

    def test_duplicate_points_error_includes_validation_type(self):
        """Test that duplicate points error includes validation type and details."""
        duplicate_points = [
            Point(0, 0),
            Point(10, 0),
            Point(10, 10),
            Point(0, 0),  # Duplicate
            Point(5, 5),
        ]

        with pytest.raises(DelaunayValidationError) as exc_info:
            validate_points(duplicate_points)

        error = exc_info.value
        assert error.validation_type == "duplicate_points"
        assert error.details.get("duplicate_indices") is not None
        assert (0, 3) in error.details.get("duplicate_indices")

    def test_wrong_point_count_error_includes_details(self):
        """Test that wrong point count error includes details."""
        insufficient_points = [
            Point(0, 0),
            Point(10, 0),
            Point(10, 10),
            Point(0, 10),
        ]

        with pytest.raises(DelaunayValidationError) as exc_info:
            validate_points(insufficient_points)

        error = exc_info.value
        assert error.validation_type == "point_count"
        assert error.details.get("expected") == 5
        assert error.details.get("received") == 4

    def test_collinear_points_error_includes_points(self):
        """Test that collinear points error includes all point coordinates."""
        collinear_points = [
            Point(0, 0),
            Point(1, 1),
            Point(2, 2),
            Point(3, 3),
            Point(4, 4),
        ]

        with pytest.raises(DelaunayValidationError) as exc_info:
            validate_points(collinear_points)

        error = exc_info.value
        assert error.validation_type == "collinear_points"
        assert "all_points" in error.details

    def test_valid_points_pass_validation(self):
        """Test that valid points pass validation without errors."""
        valid_points = [
            Point(0, 0),
            Point(10, 0),
            Point(10, 10),
            Point(0, 10),
            Point(5, 5),
        ]

        # Should not raise any exception
        validate_points(valid_points)

    def test_multiple_duplicates_are_identified(self):
        """Test that multiple duplicate pairs are identified."""
        points = [
            Point(0, 0),  # index 0
            Point(0, 0),  # index 1 - duplicate of 0
            Point(10, 10),  # index 2
            Point(10, 10),  # index 3 - duplicate of 2
            Point(5, 5),
        ]

        with pytest.raises(DelaunayValidationError) as exc_info:
            validate_points(points)

        error = exc_info.value
        duplicates = error.details.get("duplicate_indices")
        assert (0, 1) in duplicates
        assert (2, 3) in duplicates

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        duplicate_points = [
            Point(5, 5),
            Point(5, 5),
            Point(10, 0),
            Point(0, 10),
            Point(3, 3),
        ]

        with pytest.raises(DelaunayValidationError) as exc_info:
            validate_points(duplicate_points)

        error = exc_info.value
        assert "unique" in error.message.lower()
        assert "Duplicate points detected" in error.message
