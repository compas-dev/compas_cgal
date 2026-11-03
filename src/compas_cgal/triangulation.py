"""Internal CGAL adapters for the COMPAS planar-triangulation plugins."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np
from compas.tolerance import TOL

from compas_cgal import _triangulation  # type: ignore
from compas_cgal import _types_std  # type: ignore

if TYPE_CHECKING:
    from compas._typing import CoordinatesType
    from compas.geometry import ConformingDelaunay
    from compas.geometry import ConstrainedDelaunay
    from compas.geometry import Delaunay
    from compas.geometry import Frame
    from compas.geometry import Tessellation

__all__ = []


def _project_points(
    points: CoordinatesType,
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
) -> dict[tuple[float, float], list[float]]:
    coordinates: dict[tuple[float, float], list[float]] = {}
    for source, local in groups:
        for point, xy in zip(source, local, strict=True):
            coordinates.setdefault((float(xy[0]), float(xy[1])), point)
    return coordinates


def _require_minimum(points: np.ndarray, count: int, name: str) -> None:
    if len(points) < count:
        raise ValueError(f"{name} requires at least {count} points.")


def _lift_vertices(
    vertices: np.ndarray,
    frame: Frame | None,
    source_coordinates: dict[tuple[float, float], list[float]],
) -> list[list[float]]:
    from compas.geometry import Frame

    plane = Frame.worldXY() if frame is None else frame
    result = []
    for vertex in vertices:
        x = float(vertex[0])
        y = float(vertex[1])
        source = source_coordinates.get((x, y))
        if source is not None:
            result.append(source)
            continue
        result.append([plane.point[axis] + x * plane.xaxis[axis] + y * plane.yaxis[axis] for axis in range(3)])
    return result


def _triangulate_planar_points(
    points: CoordinatesType,
    *,
    strategy: Delaunay,
    frame: Frame | None = None,
) -> Tessellation:
    from compas.geometry import Delaunay
    from compas.geometry import Tessellation

    if not isinstance(strategy, Delaunay):
        raise TypeError("strategy should be a Delaunay strategy.")
    source, local = _project_points(points, frame, "Delaunay input")
    _require_minimum(local, 3, "Delaunay input")
    triangles = np.asarray(_triangulation.delaunay_triangulation(local), dtype=np.int32, order="C")
    return Tessellation(source, triangles)  # pyright: ignore[reportArgumentType]


def _triangulate_planar_domain(
    boundary: CoordinatesType,
    *,
    holes: Sequence[CoordinatesType] = (),
    constraints: Sequence[CoordinatesType] = (),
    points: CoordinatesType = (),
    strategy: ConstrainedDelaunay | ConformingDelaunay,
    frame: Frame | None = None,
) -> Tessellation:
    from compas.geometry import ConformingDelaunay
    from compas.geometry import ConstrainedDelaunay
    from compas.geometry import Tessellation

    if not isinstance(strategy, (ConstrainedDelaunay, ConformingDelaunay)):
        raise TypeError("strategy should be a ConstrainedDelaunay or ConformingDelaunay strategy.")

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
    if isinstance(strategy, ConstrainedDelaunay):
        vertices, triangles = _triangulation.constrained_delaunay_triangulation(boundary_group[1], points_group[1], holes_vector, constraints_vector, False)
    elif strategy.quality is None:
        vertices, triangles = _triangulation.constrained_delaunay_triangulation(boundary_group[1], points_group[1], holes_vector, constraints_vector, True)
    else:
        quality = strategy.quality
        unsupported = []
        if quality.min_angle is not None:
            unsupported.append("min_angle")
        if quality.max_area is not None:
            unsupported.append("max_area")
        if unsupported:
            raise NotImplementedError(f"CGAL planar refinement does not support: {', '.join(unsupported)}.")
        if quality.max_edge_length is None:
            raise NotImplementedError("CGAL planar refinement requires max_edge_length.")
        vertices, triangles = _triangulation.refined_delaunay_mesh(
            boundary_group[1],
            points_group[1],
            holes_vector,
            constraints_vector,
            0.0,
            quality.max_edge_length,
            False,
        )

    vertices = np.asarray(vertices, dtype=np.float64, order="C")
    triangles = np.asarray(triangles, dtype=np.int32, order="C")
    lifted = _lift_vertices(vertices, frame, _source_coordinates(groups))
    return Tessellation(lifted, triangles)  # pyright: ignore[reportArgumentType]
