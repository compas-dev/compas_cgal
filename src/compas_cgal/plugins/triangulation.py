"""Triangulation plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Frame
    from compas.typing import PointGroupsLike
    from compas.typing import PointsLike
    from compas.typing import VerticesFaces


@plugin(category="triangulation", requires=["compas_cgal._triangulation"])
def _delaunay_triangulation(
    points: PointsLike,
    *,
    frame: Frame | None = None,
) -> VerticesFaces:
    from compas_cgal.triangulation import delaunay_triangulation

    return delaunay_triangulation(points, frame=frame)


@plugin(category="triangulation", requires=["compas_cgal._triangulation"])
def _constrained_delaunay_triangulation(
    boundary: PointsLike,
    *,
    holes: PointGroupsLike = (),
    constraints: PointGroupsLike = (),
    points: PointsLike = (),
    frame: Frame | None = None,
) -> VerticesFaces:
    from compas_cgal.triangulation import constrained_delaunay_triangulation

    return constrained_delaunay_triangulation(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        frame=frame,
    )


@plugin(category="triangulation", requires=["compas_cgal._triangulation"])
def _conforming_delaunay_triangulation(
    boundary: PointsLike,
    *,
    holes: PointGroupsLike = (),
    constraints: PointGroupsLike = (),
    points: PointsLike = (),
    max_edge_length: float | None = None,
    frame: Frame | None = None,
) -> VerticesFaces:
    from compas_cgal.triangulation import conforming_delaunay_triangulation

    return conforming_delaunay_triangulation(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        max_edge_length=max_edge_length,
        frame=frame,
    )


__all__ = []
