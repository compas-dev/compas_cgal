"""CGAL implementations of planar Delaunay triangulation."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite
from numbers import Real
from typing import TYPE_CHECKING

import numpy as np
from compas.tolerance import TOL

from compas_cgal import _triangulation
from compas_cgal import _types_std
from compas_cgal.types import DelaunayResult

if TYPE_CHECKING:
    from compas.geometry import Frame
    from compas.typing import PointGroupsLike
    from compas.typing import PointsLike
    from compas.typing import RealInput

__all__ = [
    "conforming_delaunay_triangulation",
    "constrained_delaunay_triangulation",
    "delaunay_triangulation",
]


def _project_points(
    points: PointsLike,
    frame: Frame | None,
    name: str,
) -> tuple[list[list[float]], np.ndarray]:
    from compas.geometry import Frame
    from compas.geometry import distance_point_plane

    plane = Frame.worldXY() if frame is None else frame
    source = [[float(value) for value in point] for point in points]
    local = np.empty((len(source), 2), dtype=np.float64, order="C")
    for index, point in enumerate(source):
        if len(point) != 3:
            raise ValueError(f"{name} points should have exactly three coordinates.")
        if not all(np.isfinite(value) for value in point):
            raise ValueError(f"{name} points should contain finite coordinates.")
        if not TOL.is_zero(distance_point_plane(point, (plane.point, plane.normal))):
            location = "world XY" if frame is None else "the triangulation frame"
            raise ValueError(f"{name} points should lie on {location} within tolerance.")
        vector = [point[axis] - plane.point[axis] for axis in range(3)]
        local[index, 0] = sum(vector[axis] * plane.xaxis[axis] for axis in range(3))
        local[index, 1] = sum(vector[axis] * plane.yaxis[axis] for axis in range(3))
    return source, local


def _vector_row_matrices(items: Sequence[np.ndarray]) -> _types_std.VectorRowMatrixXd:
    vector = _types_std.VectorRowMatrixXd()
    for item in items:
        vector.append(np.asarray(item, dtype=np.float64, order="C"))
    return vector


def _source_coordinates(
    groups: Sequence[tuple[list[list[float]], np.ndarray]],
) -> list[tuple[list[float], list[float]]]:
    from compas.geometry import distance_point_point

    coordinates: list[tuple[list[float], list[float]]] = []
    for source, local in groups:
        for point, xy in zip(source, local, strict=True):
            location = [float(xy[0]), float(xy[1])]
            for known_location, known_point in coordinates:
                distance = ((location[0] - known_location[0]) ** 2 + (location[1] - known_location[1]) ** 2) ** 0.5
                if TOL.is_zero(distance):
                    if not TOL.is_zero(distance_point_point(point, known_point)):
                        raise ValueError("Points at the same planar location should have identical 3D coordinates.")
                    break
            else:
                coordinates.append((location, point))
    return coordinates


def _require_minimum(points: np.ndarray, count: int, name: str) -> None:
    if len(points) < count:
        raise ValueError(f"{name} requires at least {count} points.")


def _lift_vertices(
    vertices: np.ndarray,
    frame: Frame | None,
    source_coordinates: list[tuple[list[float], list[float]]],
) -> list[list[float]]:
    from compas.geometry import Frame

    plane = Frame.worldXY() if frame is None else frame
    result = []
    for vertex in vertices:
        x = float(vertex[0])
        y = float(vertex[1])
        for location, source in source_coordinates:
            distance = ((x - location[0]) ** 2 + (y - location[1]) ** 2) ** 0.5
            if TOL.is_zero(distance):
                result.append(source)
                break
        else:
            result.append([plane.point[axis] + x * plane.xaxis[axis] + y * plane.yaxis[axis] for axis in range(3)])
    return result


def _validated_result(
    vertices: np.ndarray,
    triangles: np.ndarray,
    frame: Frame | None,
    source_coordinates: list[tuple[list[float], list[float]]],
    *,
    allow_steiner: bool,
) -> DelaunayResult:
    vertices = np.ascontiguousarray(vertices, dtype=np.float64)
    if vertices.ndim != 2 or vertices.shape[1] not in (2, 3):
        raise RuntimeError("CGAL Delaunay result vertices should have shape (N, 2) or (N, 3).")
    if not np.isfinite(vertices[:, :2]).all():
        raise RuntimeError("CGAL Delaunay result vertices should be finite.")

    triangle_array = np.asarray(triangles)
    if triangle_array.ndim != 2 or triangle_array.shape[1] != 3:
        raise RuntimeError("CGAL Delaunay result faces should have shape (M, 3).")
    if triangle_array.dtype.kind not in "iu" or triangle_array.dtype.kind == "b":
        raise RuntimeError("CGAL Delaunay result indices should be integers.")
    info = np.iinfo(np.int32)
    if triangle_array.size and (triangle_array.min() < info.min or triangle_array.max() > info.max):
        raise RuntimeError("CGAL Delaunay result indices exceed the supported range.")
    triangle_array = np.ascontiguousarray(triangle_array, dtype=np.int32)

    xy = vertices[:, :2]
    if triangle_array.size:
        if triangle_array.min() < 0 or triangle_array.max() >= len(vertices):
            raise RuntimeError("CGAL Delaunay result indices should be in range.")
        for triangle in triangle_array:
            if len(set(int(index) for index in triangle)) != 3:
                raise RuntimeError("CGAL Delaunay result triangles should use three distinct vertices.")
            a, b, c = xy[triangle]
            signed_area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if TOL.is_zero(float(signed_area)):
                raise RuntimeError("CGAL Delaunay result should not contain degenerate triangles.")
            if signed_area < 0:
                triangle[1], triangle[2] = triangle[2], triangle[1]

    lifted = _lift_vertices(vertices, frame, source_coordinates)
    for location, source in source_coordinates:
        if not any(TOL.is_zero(((float(vertex[0]) - location[0]) ** 2 + (float(vertex[1]) - location[1]) ** 2) ** 0.5) for vertex in xy):
            raise RuntimeError(f"CGAL Delaunay result omitted source coordinate {source!r}.")
    if not allow_steiner and len(lifted) != len(source_coordinates):
        raise RuntimeError("CGAL Delaunay result unexpectedly inserted vertices.")
    return lifted, triangle_array


def delaunay_triangulation(
    points: PointsLike,
    *,
    frame: Frame | None = None,
) -> DelaunayResult:
    """Construct a planar Delaunay triangulation of points.

    Parameters
    ----------
    points
        Planar XYZ coordinates.
    frame
        The plane in which to interpret the coordinates. If `None`, use world
        XY.

    Returns
    -------
    tuple[list[list[float]], numpy.ndarray]
        Preserved XYZ coordinates and a C-contiguous `int32` triangle array.
        Repeated planar locations are coalesced and no vertices are inserted.

    """

    source, local = _project_points(points, frame, "Delaunay input")
    source_coordinates = _source_coordinates([(source, local)])
    if len(source_coordinates) < 3:
        raise ValueError("Delaunay input requires at least 3 distinct points.")
    local = np.ascontiguousarray([location for location, _ in source_coordinates], dtype=np.float64)
    triangles = _triangulation.delaunay_triangulation(local)
    return _validated_result(local, triangles, frame, source_coordinates, allow_steiner=False)


def constrained_delaunay_triangulation(
    boundary: PointsLike,
    *,
    holes: PointGroupsLike = (),
    constraints: PointGroupsLike = (),
    points: PointsLike = (),
    frame: Frame | None = None,
) -> DelaunayResult:
    """Triangulate a constrained planar domain without inserting vertices.

    Parameters
    ----------
    boundary
        The exterior planar boundary.
    holes
        Closed interior boundaries.
    constraints
        Open constrained polylines.
    points
        Additional interior points.
    frame
        The plane in which to interpret the coordinates. If `None`, use world
        XY.

    Returns
    -------
    tuple[list[list[float]], numpy.ndarray]
        Preserved XYZ coordinates and a C-contiguous `int32` triangle array.

    """
    return _triangulate_domain(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        max_edge_length=None,
        conforming=False,
        frame=frame,
    )


def conforming_delaunay_triangulation(
    boundary: PointsLike,
    *,
    holes: PointGroupsLike = (),
    constraints: PointGroupsLike = (),
    points: PointsLike = (),
    max_edge_length: RealInput | None = None,
    frame: Frame | None = None,
) -> DelaunayResult:
    """Triangulate and optionally refine a constrained planar domain.

    Parameters
    ----------
    boundary
        The exterior planar boundary.
    holes
        Closed interior boundaries.
    constraints
        Open constrained polylines.
    points
        Additional interior points.
    max_edge_length
        A positive finite edge-length refinement target. If `None`, only
        conform the Delaunay triangulation.
    frame
        The plane in which to interpret the coordinates. If `None`, use world
        XY.

    Returns
    -------
    tuple[list[list[float]], numpy.ndarray]
        Preserved XYZ coordinates and a C-contiguous `int32` triangle array.
        The result may contain planar Steiner vertices.

    """
    if max_edge_length is not None:
        if not isinstance(max_edge_length, Real) or isinstance(max_edge_length, bool):
            raise TypeError("max_edge_length should be a real number.")
        max_edge_length = float(max_edge_length)
        if not isfinite(max_edge_length) or max_edge_length <= 0:
            raise ValueError("max_edge_length should be positive and finite.")
    return _triangulate_domain(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        max_edge_length=max_edge_length,
        conforming=True,
        frame=frame,
    )


def _triangulate_domain(
    boundary: PointsLike,
    *,
    holes: PointGroupsLike,
    constraints: PointGroupsLike,
    points: PointsLike,
    max_edge_length: float | None,
    conforming: bool,
    frame: Frame | None,
) -> DelaunayResult:

    boundary_group = _project_points(boundary, frame, "Boundary")
    hole_groups = [_project_points(hole, frame, "Hole") for hole in holes]
    constraint_groups = [_project_points(constraint, frame, "Constraint") for constraint in constraints]
    points_group = _project_points(points, frame, "Interior")
    groups = [boundary_group, *hole_groups, *constraint_groups, points_group]

    _require_minimum(boundary_group[1], 3, "Boundary")
    for _, hole in hole_groups:
        _require_minimum(hole, 3, "Hole")
    for _, constraint in constraint_groups:
        _require_minimum(constraint, 2, "Constraint")

    holes_vector = _vector_row_matrices([group[1] for group in hole_groups])
    constraints_vector = _vector_row_matrices([group[1] for group in constraint_groups])
    if not conforming:
        vertices, triangles = _triangulation.constrained_delaunay_triangulation(boundary_group[1], points_group[1], holes_vector, constraints_vector, False)
    elif max_edge_length is None:
        vertices, triangles = _triangulation.constrained_delaunay_triangulation(boundary_group[1], points_group[1], holes_vector, constraints_vector, True)
    else:
        vertices, triangles = _triangulation.refined_delaunay_mesh(
            boundary_group[1],
            points_group[1],
            holes_vector,
            constraints_vector,
            0.0,
            max_edge_length,
            False,
        )

    source_coordinates = _source_coordinates(groups)
    return _validated_result(vertices, triangles, frame, source_coordinates, allow_steiner=conforming)
