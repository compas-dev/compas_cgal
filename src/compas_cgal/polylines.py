from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from compas_cgal._cgal import polylines as _polylines

__all__ = [
    "simplify_polylines",
    "simplify_polyline",
    "closest_points_on_polyline",
]


PointsList = Sequence[Sequence[float]]


def simplify_polylines(
    polylines: list[PointsList],
    threshold: float,
) -> list[NDArray[np.float64]]:
    """Simplify multiple polylines using Douglas-Peucker algorithm.

    Parameters
    ----------
    polylines : list[list[list[float]]]
        List of polylines, where each polyline is a list of points [x, y] or [x, y, z].
    threshold : float
        Maximum perpendicular distance from original polyline to simplified version.
        Points within this distance may be removed.

    Returns
    -------
    list[NDArray[np.float64]]
        List of simplified polylines as numpy arrays.

    Examples
    --------
    >>> polyline = [[0, 0], [1, 0.1], [2, 0], [3, 0.1], [4, 0]]
    >>> simplified = simplify_polylines([polyline], threshold=0.2)
    >>> len(simplified[0]) < len(polyline)
    True

    """
    polylines_np = [np.asarray(p, dtype=np.float64) for p in polylines]
    return _polylines.simplify_polylines(polylines_np, float(threshold))


def simplify_polyline(
    polyline: PointsList,
    threshold: float,
) -> NDArray[np.float64]:
    """Simplify a single polyline using Douglas-Peucker algorithm.

    Parameters
    ----------
    polyline : list[list[float]]
        Polyline as a list of points [x, y] or [x, y, z].
    threshold : float
        Maximum perpendicular distance from original polyline to simplified version.

    Returns
    -------
    NDArray[np.float64]
        Simplified polyline as numpy array.

    """
    result = simplify_polylines([polyline], threshold)
    return result[0] if result else np.asarray(polyline, dtype=np.float64)


def closest_points_on_polyline(
    query_points: PointsList,
    polyline: PointsList,
) -> NDArray[np.float64]:
    """Find closest points on a polyline for a batch of query points.

    Uses CGAL AABB tree for efficient O(log n) queries per point.

    Parameters
    ----------
    query_points : list[list[float]]
        Query points as list of [x, y] or [x, y, z].
    polyline : list[list[float]]
        Polyline vertices as list of [x, y] or [x, y, z].

    Returns
    -------
    NDArray[np.float64]
        Array of closest points on the polyline, one per query point.

    Examples
    --------
    >>> polyline = [[0, 0], [10, 0], [10, 10]]
    >>> queries = [[5, 5], [15, 5]]
    >>> closest = closest_points_on_polyline(queries, polyline)
    >>> closest[0]  # closest to [5, 5] is on segment [0,0]-[10,0] or [10,0]-[10,10]
    array([...])

    """
    query_np = np.asarray(query_points, dtype=np.float64)
    polyline_np = np.asarray(polyline, dtype=np.float64)
    return _polylines.closest_points_on_polyline(query_np, polyline_np)
