"""Intersection plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas._typing import CoordinatesCollectionInput
    from compas._typing import TriangleMeshInput


@plugin(category="intersections", pluggable_name="_intersection_mesh_mesh", requires=["compas_cgal"])
def _intersection_mesh_mesh(A: TriangleMeshInput, B: TriangleMeshInput) -> CoordinatesCollectionInput:
    from compas_cgal.intersections import intersection_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["_intersection_mesh_mesh"]
