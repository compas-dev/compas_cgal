"""Intersection plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.typing import VerticesFaces

    from compas_cgal.types import PolylinesNumpy


@plugin(category="intersections", pluggable_name="_intersection_mesh_mesh", requires=["compas_cgal._intersections"])
def _intersection_mesh_mesh(A: VerticesFaces, B: VerticesFaces) -> PolylinesNumpy:
    from compas_cgal.intersections import intersection_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["_intersection_mesh_mesh"]
