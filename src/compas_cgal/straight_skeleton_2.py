from typing import Tuple
from typing import Union

import numpy as np
from compas.datastructures import Graph
from compas.geometry import Polygon
from compas.geometry import normal_polygon
from compas.tolerance import TOL

from compas_cgal import _straight_skeleton_2  # type: ignore
from compas_cgal import _types_std  # noqa: F401  # type: ignore

from .types import IntNx1
from .types import IntNx2
from .types import VerticesNumpy


def graph_from_skeleton_data(points: VerticesNumpy, indices: IntNx1, edges: IntNx2, edge_types: IntNx1) -> Graph:
    """Create a graph from the skeleton data.

    Parameters
    ----------
    points
        The vertices of the skeleton, each vertex defined by 3 spatial coordinates.
    indices
        The vertex indices of the skeleton, corresponding to the points.
    edges
        The edges of the skeleton, each edge defined by 2 vertex indices.
    edge_types
        The type per edge, `0` for inner bisector, `1` for bisector, and `2` for boundary.

    Returns
    -------
    Graph
        The skeleton as a graph.
    """
    graph = Graph()
    for pt, i in zip(points, indices):
        graph.add_node(key=i, x=pt[0], y=pt[1], z=pt[2])

    for edge, etype in zip(edges, edge_types):
        edge = graph.add_edge(*edge)
        if etype == 0:
            graph.edge_attribute(edge, "inner_bisector", True)
        elif etype == 1:
            graph.edge_attribute(edge, "bisector", True)
        else:
            graph.edge_attribute(edge, "boundary", True)
    return graph


def interior_straight_skeleton(points, as_graph=True) -> Union[Graph, Tuple[VerticesNumpy, IntNx1, IntNx2, IntNx1]]:
    """Compute the skeleton of a 2D polygon.

    Parameters
    ----------
    points
        The points of the polygon.
    as_graph
        Whether the skeleton should be returned as a graph, defaults to `True`.

    Returns
    -------
    Graph | tuple[VerticesNumpy, IntNx1, IntNx2, IntNx1]
        The skeleton of the polygon.

    Raises
    ------
    ValueError
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
    """
    points = list(points)
    normal = normal_polygon(points, True)
    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")
    points, indices, edges, edge_types = _straight_skeleton_2.create_interior_straight_skeleton(V)
    if as_graph:
        return graph_from_skeleton_data(points, indices, edges, edge_types)
    return points, indices, edges, edge_types


def interior_straight_skeleton_with_holes(points, holes, as_graph=True) -> Union[Graph, Tuple[VerticesNumpy, IntNx1, IntNx2, IntNx1]]:
    """Compute the skeleton of a 2D polygon with holes.

    Parameters
    ----------
    points
        The points of the 2D polygon.
    holes
        The holes of the polygon.
    as_graph
        Whether the skeleton should be returned as a graph, defaults to `True`.

    Returns
    -------
    Graph | tuple[VerticesNumpy, IntNx1, IntNx2, IntNx1]
        The skeleton of the polygon.

    Raises
    ------
    ValueError
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
        If the normal of a hole is not directed vertically downwards like [0, 0, -1].
    """
    points = list(points)
    normal = normal_polygon(points, True)
    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")

    H = []
    for i, hole in enumerate(holes):
        points = list(hole)
        normal_hole = normal_polygon(points, True)
        if not TOL.is_allclose(normal_hole, [0, 0, -1]):
            raise ValueError("The normal of the hole should be [0, 0, -1]. The normal of the provided {}-th hole is {}".format(i, normal_hole))
        hole = np.asarray(points, dtype=np.float64)
        H.append(hole)
    points, indices, edges, edge_types = _straight_skeleton_2.create_interior_straight_skeleton_with_holes(V, H)
    if as_graph:
        return graph_from_skeleton_data(points, indices, edges, edge_types)
    return points, indices, edges, edge_types


def offset_polygon(points, offset) -> list[Polygon]:
    """Compute the offset from a 2D polygon.

    Parameters
    ----------
    points
        The points of the 2D polygon.
    offset
        The offset distance. If negative, the offset is outside the polygon, otherwise inside.

    Returns
    -------
    list[Polygon]
        The offset polygon(s).

    Raises
    ------
    ValueError
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
    """
    points = list(points)
    normal = normal_polygon(points, True)
    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")
    offset = float(offset)
    if offset < 0:  # outside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_outer(V, abs(offset))[1:]  # first one is box
    else:  # inside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_inner(V, offset)
    return [Polygon(points.tolist()) for points in offset_polygons]


def offset_polygon_with_holes(points, holes, offset) -> list[Tuple[Polygon, list[Polygon]]]:
    """Compute the offset from a 2D polygon with holes.

    Parameters
    ----------
    points
        The points of the 2D polygon.
    holes
        The holes of the polygon.
    offset
        The offset distance. If negative, the offset is outside the polygon, otherwise inside.

    Returns
    -------
    list[tuple[Polygon, list[Polygon]]]
        The polygons with holes.

    Raises
    ------
    ValueError
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
        If the normal of a hole is not directed vertically downwards like [0, 0, -1].
    """
    points = list(points)
    normal = normal_polygon(points, True)

    if TOL.is_allclose(normal, [0, 0, -1]):
        points.reverse()
        normal *= -1

    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")

    H = []
    for i, hole in enumerate(holes):
        points = hole
        normal_hole = normal_polygon(points, True)

        if TOL.is_allclose(normal_hole, [0, 0, 1]):
            points.points.reverse()
            normal_hole *= -1

        if not TOL.is_allclose(normal_hole, [0, 0, -1]):
            raise ValueError("The normal of the hole should be [0, 0, -1]. The normal of the provided {}-th hole is {}".format(i, normal_hole))

        hole = np.asarray(points, dtype=np.float64, order="C")
        H.append(hole)

    if offset < 0:  # outside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_outer_with_holes(V, H, abs(offset))
    else:  # inside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_inner_with_holes(V, H, offset)

    result = []
    for points_list in offset_polygons:
        polygon = Polygon(points_list[0].tolist())
        holes = []
        for hole in points_list[1:]:
            holes.append(Polygon(hole.tolist()))
        result.append((polygon, holes))
    return result


def weighted_offset_polygon(points, offset, weights) -> list[Polygon]:
    """Compute the offset from a 2D polygon with weights.

    Parameters
    ----------
    points
        The points of the 2D polygon.
    offset
        The offset distance. If negative, the offset is outside the polygon, otherwise inside.
    weights
        The weights for each edge, starting with the edge between the last and the first point.

    Returns
    -------
    list[Polygon]
        The offset polygon(s).

    Raises
    ------
    ValueError
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
    ValueError
        If the number of weights does not match the number of points.
    """
    points = list(points)
    normal = normal_polygon(points, True)
    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))

    V = np.asarray(points, dtype=np.float64, order="C")
    offset = float(offset)
    # Reshape weights to be a column vector (n x 1)
    W = np.asarray(weights, dtype=np.float64, order="C").reshape(-1, 1)
    if W.shape[0] != V.shape[0]:
        raise ValueError("The number of weights should be equal to the number of points %d != %d." % (W.shape[0], V.shape[0]))
    if offset < 0:
        offset_polygons = _straight_skeleton_2.create_weighted_offset_polygons_2_outer(V, abs(offset), W)
        # Return all except the first polygon which is the bounding box
        return [Polygon(points.tolist()) for points in offset_polygons[1:]]
    else:
        offset_polygons = _straight_skeleton_2.create_weighted_offset_polygons_2_inner(V, offset, W)
        return [Polygon(points.tolist()) for points in offset_polygons]
