"""Triangulation plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas._typing import CoordinatesCollectionInput
    from compas._typing import CoordinatesInput
    from compas.geometry import ConformingDelaunay
    from compas.geometry import ConstrainedDelaunay
    from compas.geometry import Delaunay
    from compas.geometry import Frame
    from compas.geometry import Tessellation


@plugin(category="triangulation", requires=["compas_cgal"])
def _triangulate_planar_points(
    points: CoordinatesInput,
    *,
    strategy: Delaunay,
    frame: Frame | None = None,
) -> Tessellation:
    from compas_cgal.triangulation import _triangulate_planar_points as implementation

    return implementation(points, strategy=strategy, frame=frame)


@plugin(category="triangulation", requires=["compas_cgal"])
def _triangulate_planar_domain(
    boundary: CoordinatesInput,
    *,
    holes: CoordinatesCollectionInput = (),
    constraints: CoordinatesCollectionInput = (),
    points: CoordinatesInput = (),
    strategy: ConstrainedDelaunay | ConformingDelaunay,
    frame: Frame | None = None,
) -> Tessellation:
    from compas_cgal.triangulation import _triangulate_planar_domain as implementation

    return implementation(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        strategy=strategy,
        frame=frame,
    )


__all__ = []
