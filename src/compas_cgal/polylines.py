"""Polyline utilities using CGAL."""

from typing import Sequence

import numpy as np
from compas.typing import Float64Array
from compas.typing import PointsLike

from compas_cgal import _types_std  # noqa: F401
from compas_cgal._polylines import closest_points_on_polyline as _closest_points
from compas_cgal._polylines import simplify_polylines as _simplify
from compas_cgal.types import PolylinesNumpy

__all__ = ["closest_points_on_polyline", "simplify_polyline", "simplify_polylines"]


def _as_polyline(points: PointsLike, name: str) -> Float64Array:
    """Convert structural points to a native 2D or 3D polyline array."""
    array = np.ascontiguousarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] not in (2, 3):
        raise ValueError(f"{name} should have shape (N, 2) or (N, 3).")
    return array


def _validate_polyline(result: Float64Array, operation: str, columns: int, rows: int | None = None) -> Float64Array:
    """Check a native polyline result against the input dimensionality."""
    if result.ndim != 2 or result.shape[1] != columns:
        raise RuntimeError(f"CGAL {operation} result should have shape (N, {columns}).")
    if rows is not None and len(result) != rows:
        raise RuntimeError(f"CGAL {operation} result should contain {rows} points, got {len(result)}.")
    return result


def simplify_polylines(polylines: Sequence[PointsLike], threshold: float) -> PolylinesNumpy:
    """Simplify multiple polylines using Douglas-Peucker algorithm.

    Simplification is performed in the XY plane only. For 3D polylines,
    Z coordinates are preserved but not considered in distance calculations.

    Parameters
    ----------
    polylines
        List of polylines. Each polyline is a sequence of 2D or 3D points.
    threshold
        Distance threshold for simplification. Higher values remove more points.

    Returns
    -------
    list of ndarray
        Simplified polylines as numpy arrays.

    Raises
    ------
    ValueError
        If an input polyline does not have two or three coordinates per point.

    Examples
    --------
    >>> polylines = [[[0, 0], [1, 0.01], [2, 0]], [[0, 0], [0, 1], [1, 1]]]
    >>> simplified = simplify_polylines(polylines, threshold=0.1)
    >>> len(simplified[0])  # First polyline simplified
    2
    >>> len(simplified[1])  # Second has corner, preserved
    3

    """
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    arrays = [_as_polyline(polyline, f"polylines[{index}]") for index, polyline in enumerate(polylines)]
    result = _simplify(arrays, threshold)
    if len(result) != len(arrays):
        raise RuntimeError(f"CGAL polyline simplification returned {len(result)} polylines for {len(arrays)} inputs.")
    for index, (points, source) in enumerate(zip(result, arrays)):
        _validate_polyline(points, f"polyline simplification item {index}", columns=source.shape[1])
    return result


def simplify_polyline(polyline: PointsLike, threshold: float) -> Float64Array:
    """Simplify a single polyline using Douglas-Peucker algorithm.

    Simplification is performed in the XY plane only. For 3D polylines,
    Z coordinates are preserved but not considered in distance calculations.

    Parameters
    ----------
    polyline
        Sequence of 2D or 3D points.
    threshold
        Distance threshold for simplification.

    Returns
    -------
    ndarray
        Simplified polyline as numpy array.

    Raises
    ------
    ValueError
        If the polyline does not have two or three coordinates per point.

    """
    result = simplify_polylines([polyline], threshold)
    return result[0]


def closest_points_on_polyline(query_points: PointsLike, polyline: PointsLike) -> Float64Array:
    """Find closest points on a polyline for a batch of query points.

    Uses CGAL's AABB tree for efficient batch queries.

    Parameters
    ----------
    query_points
        Query points as Mx2 or Mx3 array.
    polyline
        Polyline as Nx2 or Nx3 array.

    Returns
    -------
    ndarray
        Closest points on the polyline (same shape as query_points).

    Raises
    ------
    ValueError
        If either input does not have two or three coordinates per point, or
        if their coordinate dimensions differ.

    Examples
    --------
    >>> polyline = [[0, 0], [10, 0]]
    >>> queries = [[5, 5], [3, -2]]
    >>> closest = closest_points_on_polyline(queries, polyline)
    >>> closest[0]  # Closest to (5, 5) on horizontal line
    array([5., 0.])

    """
    queries = _as_polyline(query_points, "query_points")
    poly = _as_polyline(polyline, "polyline")
    if queries.shape[1] != poly.shape[1]:
        raise ValueError("query_points and polyline should have the same coordinate dimension.")
    result = _closest_points(queries, poly)
    return _validate_polyline(result, "closest-point", columns=queries.shape[1], rows=len(queries))
