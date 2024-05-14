import numpy as np
from compas.geometry import normal_polygon
from compas.tolerance import TOL

from compas_cgal._cgal import straight_skeleton_2

from .types import PolylinesNumpy


def create_interior_straight_skeleton(points) -> PolylinesNumpy:
    """Compute the skeleton of a polygon.

    Parameters
    ----------
    points : list of point coordinates or :class:`compas.geometry.Polygon`
        The points of the polygon.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        The skeleton of the polygon.

    Raises
    ------
    ValueError
        If the normal of the polygon is not [0, 0, 1].
    """
    points = list(points)
    if not TOL.is_allclose(normal_polygon(points, True), [0, 0, 1]):
        raise ValueError("Please pass a polygon with a normal vector of [0, 0, 1].")
    V = np.asarray(points, dtype=np.float64)
    return straight_skeleton_2.create_interior_straight_skeleton(V)


def create_interior_straight_skeleton_with_holes(points, holes) -> PolylinesNumpy:
    """Compute the skeleton of a polygon with holes.

    Parameters
    ----------
    points : list of point coordinates or :class:`compas.geometry.Polygon`
        The points of the polygon.
    holes : list of list of point coordinates or list of :class:`compas.geometry.Polygon`
        The holes of the polygon.

    Returns
    -------
    :attr:`compas_cgal.types.PolylinesNumpy`
        The skeleton of the polygon.

    Raises
    ------
    ValueError
        If the normal of the polygon is not [0, 0, 1].
        If the normal of a hole is not [0, 0, -1].
    """
    points = list(points)
    if not TOL.is_allclose(normal_polygon(points, True), [0, 0, 1]):
        raise ValueError("Please pass a polygon with a normal vector of [0, 0, 1].")
    V = np.asarray(points, dtype=np.float64)

    H = []
    for hole in holes:
        points = list(hole)
        if not TOL.is_allclose(normal_polygon(points, True), [0, 0, -1]):
            raise ValueError("Please pass a hole with a normal vector of [0, 0, -1].")
        hole = np.asarray(points, dtype=np.float64)
        H.append(hole)
    return straight_skeleton_2.create_interior_straight_skeleton_with_holes(V, H)
