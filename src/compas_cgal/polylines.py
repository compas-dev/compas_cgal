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
    arrays = [np.ascontiguousarray(p, dtype=np.float64) for p in polylines]
    return _simplify(arrays, threshold)


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

    Examples
    --------
    >>> polyline = [[0, 0], [10, 0]]
    >>> queries = [[5, 5], [3, -2]]
    >>> closest = closest_points_on_polyline(queries, polyline)
    >>> closest[0]  # Closest to (5, 5) on horizontal line
    array([5., 0.])

    """
    queries = np.ascontiguousarray(query_points, dtype=np.float64)
    poly = np.ascontiguousarray(polyline, dtype=np.float64)
    return _closest_points(queries, poly)
