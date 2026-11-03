"""Intersection plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Tessellation

    from compas_cgal.types import PolylinesNumpy


@plugin(category="intersections", requires=["compas_cgal"])
def intersection_mesh_mesh(A: Tessellation, B: Tessellation) -> PolylinesNumpy:
    from compas_cgal.intersections import intersection_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["intersection_mesh_mesh"]
