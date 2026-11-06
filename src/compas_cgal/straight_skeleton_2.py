import math
from collections.abc import Sequence
from numbers import Real
from typing import Literal
from typing import SupportsFloat
from typing import overload

import numpy as np
from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Polygon
from compas.geometry import earclip_polygon
from compas.geometry import normal_polygon
from compas.tolerance import TOL
from compas.typing import FloatSequenceLike
from compas.typing import PointsLike
from compas.typing import RealInput

from compas_cgal import _straight_skeleton_2
from compas_cgal import _types_std  # noqa: F401

from .types import IntNx2
from .types import SkeletonData
from .types import VerticesNumpy

type ContourSpeeds = RealInput | FloatSequenceLike | Sequence[FloatSequenceLike]

__all__ = [
    "extrude",
    "graph_from_skeleton_data",
    "interior_straight_skeleton",
    "interior_straight_skeleton_with_holes",
    "offset_polygon",
    "offset_polygon_with_holes",
    "weighted_offset_polygon",
]


def _validate_skeleton_data(result: SkeletonData, operation: str) -> SkeletonData:
    """Check the paired vectors returned by native straight-skeleton calls."""
    if len(result) != 4:
        raise RuntimeError(f"CGAL {operation} should return points, point indices, edges, and edge types.")
    points, indices, edges, edge_types = result
    if points.ndim != 2 or points.shape[1] != 3:
        raise RuntimeError(f"CGAL {operation} points should have shape (N, 3).")
    if len(indices) != len(points):
        raise RuntimeError(f"CGAL {operation} returned {len(points)} points and {len(indices)} point indices.")
    if edges.ndim != 2 or edges.shape[1] != 2:
        raise RuntimeError(f"CGAL {operation} edges should have shape (M, 2).")
    if len(edge_types) != len(edges):
        raise RuntimeError(f"CGAL {operation} returned {len(edges)} edges and {len(edge_types)} edge types.")
    return result


def graph_from_skeleton_data(points: VerticesNumpy, indices: Sequence[int], edges: IntNx2, edge_types: Sequence[int]) -> Graph:
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


@overload
def interior_straight_skeleton(points: PointsLike, as_graph: Literal[True] = True) -> Graph: ...


@overload
def interior_straight_skeleton(points: PointsLike, as_graph: Literal[False]) -> SkeletonData: ...


def interior_straight_skeleton(points: PointsLike, as_graph: bool = True) -> Graph | SkeletonData:
    """Compute the skeleton of a 2D polygon.

    Parameters
    ----------
    points
        The points of the polygon.
    as_graph
        Whether the skeleton should be returned as a graph, defaults to `True`.

    Returns
    -------
    Graph | SkeletonData
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
    points, indices, edges, edge_types = _validate_skeleton_data(
        _straight_skeleton_2.create_interior_straight_skeleton(V),
        "interior straight skeleton",
    )
    if as_graph:
        return graph_from_skeleton_data(points, indices, edges, edge_types)
    return points, indices, edges, edge_types


@overload
def interior_straight_skeleton_with_holes(points: PointsLike, holes: Sequence[PointsLike], as_graph: Literal[True] = True) -> Graph: ...


@overload
def interior_straight_skeleton_with_holes(points: PointsLike, holes: Sequence[PointsLike], as_graph: Literal[False]) -> SkeletonData: ...


def interior_straight_skeleton_with_holes(points: PointsLike, holes: Sequence[PointsLike], as_graph: bool = True) -> Graph | SkeletonData:
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
    Graph | SkeletonData
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
        hole = np.ascontiguousarray(points, dtype=np.float64)
        H.append(hole)
    points, indices, edges, edge_types = _validate_skeleton_data(
        _straight_skeleton_2.create_interior_straight_skeleton_with_holes(V, H),
        "interior straight skeleton with holes",
    )
    if as_graph:
        return graph_from_skeleton_data(points, indices, edges, edge_types)
    return points, indices, edges, edge_types


def offset_polygon(points: PointsLike, offset: SupportsFloat) -> list[Polygon]:
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
    return [Polygon(points) for points in offset_polygons]


def offset_polygon_with_holes(points: PointsLike, holes: Sequence[PointsLike], offset: RealInput) -> list[tuple[Polygon, list[Polygon]]]:
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
    points = list(points.points) if isinstance(points, Polygon) else list(points)
    normal = normal_polygon(points, True)

    if TOL.is_allclose(normal, [0, 0, -1]):
        points.reverse()
        normal = [0.0, 0.0, 1.0]

    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")

    H = []
    for i, hole in enumerate(holes):
        hole_points = list(hole.points) if isinstance(hole, Polygon) else list(hole)
        normal_hole = normal_polygon(hole_points, True)

        if TOL.is_allclose(normal_hole, [0, 0, 1]):
            hole_points.reverse()
            normal_hole = [0.0, 0.0, -1.0]

        if not TOL.is_allclose(normal_hole, [0, 0, -1]):
            raise ValueError("The normal of the hole should be [0, 0, -1]. The normal of the provided {}-th hole is {}".format(i, normal_hole))

        H.append(np.asarray(hole_points, dtype=np.float64, order="C"))

    if offset < 0:  # outside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_outer_with_holes(V, H, float(abs(offset)))
    else:  # inside
        offset_polygons = _straight_skeleton_2.create_offset_polygons_2_inner_with_holes(V, H, float(offset))

    result = []
    for points_list in offset_polygons:
        polygon = Polygon(points_list[0])
        holes = []
        for hole in points_list[1:]:
            holes.append(Polygon(hole))
        result.append((polygon, holes))
    return result


def weighted_offset_polygon(points: PointsLike, offset: SupportsFloat, weights: FloatSequenceLike) -> list[Polygon]:
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
        return [Polygon(points) for points in offset_polygons[1:]]
    else:
        offset_polygons = _straight_skeleton_2.create_weighted_offset_polygons_2_inner(V, offset, W)
        return [Polygon(points) for points in offset_polygons]


def _contour_speeds(value, sizes, name):
    """Expand a speed specification into a per-contour, per-edge structure.

    Parameters
    ----------
    value : float | sequence
        A single value applied to every edge, one value per edge across all
        contours, or one sequence of edge values per contour.
    sizes : list[int]
        The number of edges of each contour (outer boundary first, then holes).
    name : str
        The name of the quantity, used for error messages.

    Returns
    -------
    list[list[float]]
        One list of edge values per contour.
    """
    if isinstance(value, Real):
        return [[float(value)] * n for n in sizes]

    value = list(value)

    # One sequence of edge values per contour.
    if len(value) == len(sizes) and all(hasattr(item, "__len__") and not isinstance(item, (str, bytes)) for item in value):
        speeds = []
        for item, n in zip(value, sizes):
            item = [float(x) for x in item]
            if len(item) != n:
                raise ValueError("The number of {} for a contour ({}) does not match its number of edges ({}).".format(name, len(item), n))
            speeds.append(item)
        return speeds

    # A flat list with one value per edge across all contours.
    flat = [float(x) for x in value]
    total = sum(sizes)
    if len(flat) == total:
        speeds = []
        start = 0
        for n in sizes:
            speeds.append(flat[start : start + n])
            start += n
        return speeds

    raise ValueError(
        "The number of {} ({}) should be a single value, one value per edge ({} total), or one list of values per contour ({}).".format(name, len(flat), total, len(sizes))
    )


def _roof_outline(mesh: Mesh, angle_tol: float = 1.0) -> list[Line]:
    """Return the roof lines of a mesh: the edges between non-coplanar faces.

    These are the eaves, hips and ridges. Coplanar diagonals (for example those from a
    triangulated base with courtyards) are skipped, so only the true roof lines remain.
    """
    cos_tol = math.cos(math.radians(angle_tol))
    lines = []
    for edge in mesh.edges():
        face_1, face_2 = mesh.edge_faces(edge)
        if face_1 is None or face_2 is None or mesh.face_normal(face_1).dot(mesh.face_normal(face_2)) < cos_tol:
            lines.append(mesh.edge_line(edge))
    return lines


def _triangulated(mesh: Mesh) -> Mesh:
    """Ear-clip the polygon faces of a mesh into triangles, preserving orientation.

    compas_viewer (and many renderers) fan-triangulate an n-gon from its centroid, which
    is wrong for non-convex faces. Ear-clipping keeps the fill correct while the true
    polygon edges are drawn separately as the roof outline. Each ear triangle is wound to
    match its face normal so the triangulated mesh stays closed.
    """
    vertices, _ = mesh.to_vertices_and_faces()
    triangles = []
    for face in mesh.faces():
        face_vertices = mesh.face_vertices(face)
        if len(face_vertices) == 3:
            triangles.append(face_vertices)
            continue
        normal = mesh.face_normal(face)
        polygon = Polygon([vertices[key] for key in face_vertices])
        for a, b, c in earclip_polygon(polygon):
            triangle = [face_vertices[a], face_vertices[b], face_vertices[c]]
            points = [vertices[key] for key in triangle]
            if normal.dot(normal_polygon(points)) < 0:
                triangle.reverse()
            triangles.append(triangle)
    return Mesh.from_vertices_and_faces(vertices, triangles)


def extrude(
    points: PointsLike,
    holes: Sequence[PointsLike] | None = None,
    weights: ContourSpeeds | None = None,
    angles: ContourSpeeds | None = None,
    maximum_height: SupportsFloat | None = None,
) -> tuple[Mesh, list[Line]]:
    """Extrude a 2D polygon into a closed 3D roof mesh using the straight skeleton.

    This turns a building footprint into roof-like geometry. Each contour edge sweeps
    inwards (and upwards) at a speed controlled by either straight skeleton weights or
    taper angles. A uniform weight of `1` (or an angle of `45` degrees) produces a
    standard 45 degree hip roof.

    The result is ready to display: the returned mesh is triangulated so it renders
    correctly (even for non-convex roof faces), and the returned lines are the true roof
    edges (eaves, hips and ridges) to draw on top. A minimal visualization is::

        mesh, lines = extrude(polygon, angles=45.0)
        viewer.scene.add(mesh, show_lines=False)
        for line in lines:
            viewer.scene.add(line)

    Parameters
    ----------
    points : sequence[point] | Polygon
        The points of the outer boundary polygon.
    holes : sequence[sequence[point]], optional
        The holes of the polygon, each as a sequence of points.
    weights : float | sequence, optional
        Straight skeleton edge weights. A single value applied to every edge, one value
        per edge across all contours, or one sequence of edge values per contour
        (outer boundary first, then holes). Mutually exclusive with `angles`.
    angles : float | sequence, optional
        Taper angles in degrees, following the same shape rules as `weights`. An angle
        of `45` corresponds to a weight of `1`. Mutually exclusive with `weights`.
    maximum_height : float, optional
        The maximum extrusion height. If not provided, an inward slope is extruded up to
        the apex of the skeleton. A maximum height is required for outward or vertical
        slopes (weights that are negative, or angles of 90 degrees or more).

    Returns
    -------
    tuple[Mesh, list[Line]]
        The triangulated, closed roof mesh (ready to display with hidden edges), and the
        roof outline as a list of line segments (eaves, hips and ridges).

    Raises
    ------
    ValueError
        If both `weights` and `angles` are provided.
        If the normal of the polygon is not directed vertically upwards like [0, 0, 1].
        If the normal of a hole is not directed vertically downwards like [0, 0, -1].
    RuntimeError
        If CGAL fails to extrude the skeleton.
    """
    if weights is not None and angles is not None:
        raise ValueError("Provide either `weights` or `angles`, not both.")

    # The outer boundary must be counter-clockwise (normal pointing up).
    points = list(points)
    normal = normal_polygon(points, True)
    if TOL.is_allclose(normal, [0, 0, -1]):
        points.reverse()
        normal = normal_polygon(points, True)
    if not TOL.is_allclose(normal, [0, 0, 1]):
        raise ValueError("The normal of the polygon should be [0, 0, 1]. The normal of the provided polygon is {}".format(normal))
    V = np.asarray(points, dtype=np.float64, order="C")

    # The holes must be clockwise (normal pointing down).
    H = []
    hole_sizes = []
    for i, hole in enumerate(holes or []):
        hole_points = list(hole)
        hole_normal = normal_polygon(hole_points, True)
        if TOL.is_allclose(hole_normal, [0, 0, 1]):
            hole_points.reverse()
            hole_normal = normal_polygon(hole_points, True)
        if not TOL.is_allclose(hole_normal, [0, 0, -1]):
            raise ValueError("The normal of the hole should be [0, 0, -1]. The normal of the provided {}-th hole is {}".format(i, hole_normal))
        H.append(np.asarray(hole_points, dtype=np.float64, order="C"))
        hole_sizes.append(len(hole_points))

    sizes = [len(points)] + hole_sizes

    if angles is not None:
        use_angles = True
        speeds = _contour_speeds(angles, sizes, "angles")
    elif weights is not None:
        use_angles = False
        speeds = _contour_speeds(weights, sizes, "weights")
    else:
        # A uniform weight of 1 corresponds to a 45 degree slope.
        use_angles = False
        speeds = [[1.0] * n for n in sizes]

    max_height = float(maximum_height) if maximum_height is not None else -1.0

    vertices, faces = _straight_skeleton_2.extrude_straight_skeleton(V, H, speeds, use_angles, max_height)
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    return _triangulated(mesh), _roof_outline(mesh)
