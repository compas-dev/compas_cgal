import numpy as np
from compas.geometry import Polygon
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


def create_offset_polygons_2(points, offset):
    """Compute the polygon offset.

    Parameters
    ----------
    points : list of point coordinates or :class:`compas.geometry.Polygon`
        The points of the polygon.
    offset : float
        The offset distance. If negative, the offset is outside the polygon, otherwise inside.

    Returns
    -------
    list of Polygon
        The offset polygon(s).

    Raises
    ------
    ValueError
        If the normal of the polygon is not [0, 0, 1].
    """
    points = list(points)
    if not TOL.is_allclose(normal_polygon(points, True), [0, 0, 1]):
        raise ValueError("Please pass a polygon with a normal vector of [0, 0, 1].")
    V = np.asarray(points, dtype=np.float64)
    offset = float(offset)
    if offset < 0:  # outside
        offset_polygons = straight_skeleton_2.create_offset_polygons_2_outer(V, abs(offset))[1:]  # first one is box
    else:  # inside
        offset_polygons = straight_skeleton_2.create_offset_polygons_2_inner(V, offset)
    return [Polygon(points.tolist()) for points in offset_polygons]


def create_weighted_offset_polygons_2(points, offset, weights):
    """Compute the polygon offset with weights.

    Parameters
    ----------
    points : list of point coordinates or :class:`compas.geometry.Polygon`
        The points of the polygon.
    offset : float
        The offset distance. If negative, the offset is outside the polygon, otherwise inside.
    weights : list of float
        The weights for each edge, starting with the edge between the last and the first point.

    Returns
    -------
    list of Polygon
        The offset polygon(s).

    Raises
    ------
    ValueError
        If the normal of the polygon is not [0, 0, 1].
    ValueError
        If the number of weights do not match the number of points.
    """
    points = list(points)
    if not TOL.is_allclose(normal_polygon(points, True), [0, 0, 1]):
        raise ValueError("Please pass a polygon with a normal vector of [0, 0, 1].")
    V = np.asarray(points, dtype=np.float64)
    offset = float(offset)
    W = np.asarray(weights, dtype=np.float64)
    if W.shape[0] != V.shape[0]:
        raise ValueError("The number of weights should be equal to the number of points %d != %d." % (W.shape[0], V.shape[0]))
    if offset < 0:
        offset_polygons = straight_skeleton_2.create_weighted_offset_polygons_2_outer(V, abs(offset), W)[1:]
    else:
        offset_polygons = straight_skeleton_2.create_weighted_offset_polygons_2_inner(V, offset, W)
    return [Polygon(points.tolist()) for points in offset_polygons]
