import numpy as np
import pytest

from compas_cgal.polylines import closest_points_on_polyline
from compas_cgal.polylines import simplify_polyline
from compas_cgal.polylines import simplify_polylines


class TestSimplifyPolyline:
    """Tests for polyline simplification using Douglas-Peucker algorithm."""

    def test_simplify_straight_line_with_noise(self):
        """Points along a line with small deviations should be simplified."""
        polyline = [
            [0, 0],
            [1, 0.01],
            [2, -0.01],
            [3, 0.02],
            [4, 0],
        ]
        result = simplify_polyline(polyline, threshold=0.1)
        # Should simplify to just start and end
        assert len(result) == 2
        assert np.allclose(result[0], [0, 0])
        assert np.allclose(result[1], [4, 0])

    def test_simplify_preserves_corners(self):
        """Sharp corners should be preserved during simplification."""
        # L-shaped polyline
        polyline = [
            [0, 0],
            [5, 0],
            [5, 5],
        ]
        result = simplify_polyline(polyline, threshold=0.1)
        # All 3 points should be preserved (corner is important)
        assert len(result) == 3

    def test_simplify_with_z_coords(self):
        """Simplification should work with 3D points (z preserved)."""
        polyline = [
            [0, 0, 1],
            [1, 0.01, 2],
            [2, 0, 3],
        ]
        result = simplify_polyline(polyline, threshold=0.1)
        assert result.shape[1] == 3  # Preserves 3 columns
        assert len(result) == 2  # Middle point removed

    def test_simplify_short_polyline(self):
        """Polylines with less than 3 points should be returned unchanged."""
        polyline = [[0, 0], [1, 1]]
        result = simplify_polyline(polyline, threshold=0.1)
        assert len(result) == 2

    def test_simplify_multiple_polylines(self):
        """Batch simplification of multiple polylines."""
        polylines = [
            [[0, 0], [1, 0.01], [2, 0]],
            [[0, 0], [0, 1], [1, 1]],
        ]
        results = simplify_polylines(polylines, threshold=0.1)
        assert len(results) == 2
        assert len(results[0]) == 2  # First simplified
        assert len(results[1]) == 3  # Second has corner, preserved


class TestClosestPointsOnPolyline:
    """Tests for batch closest point queries on polylines."""

    def test_closest_point_on_segment(self):
        """Find closest points on a single segment."""
        polyline = [[0, 0], [10, 0]]
        queries = [[5, 5]]
        result = closest_points_on_polyline(queries, polyline)
        # Closest point on horizontal segment to (5, 5) is (5, 0)
        assert np.allclose(result[0], [5, 0], atol=1e-6)

    def test_closest_point_at_vertex(self):
        """Query point closest to a polyline vertex."""
        polyline = [[0, 0], [10, 0], [10, 10]]
        queries = [[10, 5]]
        result = closest_points_on_polyline(queries, polyline)
        # Point (10, 5) is on the second segment
        assert np.allclose(result[0], [10, 5], atol=1e-6)

    def test_closest_point_batch(self):
        """Batch query multiple points."""
        polyline = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
        queries = [
            [5, -5],   # Closest to bottom edge
            [15, 5],   # Closest to right edge
            [5, 15],   # Closest to top edge
            [-5, 5],   # Closest to left edge
        ]
        result = closest_points_on_polyline(queries, polyline)
        assert len(result) == 4
        assert np.allclose(result[0], [5, 0], atol=1e-6)   # Bottom
        assert np.allclose(result[1], [10, 5], atol=1e-6)  # Right
        assert np.allclose(result[2], [5, 10], atol=1e-6)  # Top
        assert np.allclose(result[3], [0, 5], atol=1e-6)   # Left

    def test_closest_point_single_point_polyline(self):
        """Degenerate case: polyline is a single point."""
        polyline = [[5, 5]]
        queries = [[0, 0], [10, 10]]
        result = closest_points_on_polyline(queries, polyline)
        # All closest points should be the single polyline point
        assert np.allclose(result[0], [5, 5])
        assert np.allclose(result[1], [5, 5])

    def test_closest_point_returns_correct_shape(self):
        """Output shape should match input query shape."""
        polyline = [[0, 0], [10, 0]]
        queries = [[1, 1], [2, 2], [3, 3]]
        result = closest_points_on_polyline(queries, polyline)
        assert result.shape == (3, 2)
