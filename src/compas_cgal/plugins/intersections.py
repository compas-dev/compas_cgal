"""Intersection plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas_cgal.types import PolylinesNumpy
    from compas_cgal.types import VerticesFaces


@plugin(category="intersections", requires=["compas_cgal"])
def intersection_mesh_mesh(A: VerticesFaces, B: VerticesFaces) -> PolylinesNumpy:
    from compas_cgal.intersections import intersection_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["intersection_mesh_mesh"]
