"""Polyline utilities using CGAL."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from compas_cgal import _types_std  # noqa: F401  # Load vector type bindings
from compas_cgal._polylines import closest_points_on_polyline as _closest_points
from compas_cgal._polylines import simplify_polylines as _simplify

if TYPE_CHECKING:
    PointsList = list[list[float]] | NDArray


__all__ = ["simplify_polylines", "simplify_polyline", "closest_points_on_polyline"]


def simplify_polylines(polylines: list[PointsList], threshold: float) -> list[NDArray]:
    """Simplify multiple polylines using Douglas-Peucker algorithm.

    Parameters
    ----------
    polylines : list of array-like
        List of polylines. Each polyline is a sequence of 2D or 3D points.
    threshold : float
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
    arrays = [np.asarray(p, dtype=np.float64) for p in polylines]
    return _simplify(arrays, threshold)


def simplify_polyline(polyline: PointsList, threshold: float) -> NDArray:
    """Simplify a single polyline using Douglas-Peucker algorithm.

    Parameters
    ----------
    polyline : array-like
        Sequence of 2D or 3D points.
    threshold : float
        Distance threshold for simplification.

    Returns
    -------
    ndarray
        Simplified polyline as numpy array.

    """
    result = simplify_polylines([polyline], threshold)
    return result[0]


def closest_points_on_polyline(query_points: PointsList, polyline: PointsList) -> NDArray:
    """Find closest points on a polyline for a batch of query points.

    Uses CGAL's AABB tree for efficient batch queries.

    Parameters
    ----------
    query_points : array-like
        Query points as Mx2 or Mx3 array.
    polyline : array-like
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
    queries = np.asarray(query_points, dtype=np.float64)
    poly = np.asarray(polyline, dtype=np.float64)
    return _closest_points(queries, poly)
