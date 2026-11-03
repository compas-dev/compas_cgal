"""Boolean plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Tessellation

    from compas_cgal.types import VerticesFaces
    from compas_cgal.types import VerticesFacesNumpy


@plugin(category="booleans", pluggable_name="boolean_union_mesh_mesh", requires=["compas_cgal"])
def boolean_union_mesh_mesh(A: Tessellation, B: Tessellation) -> Tessellation:
    from compas_cgal.booleans import boolean_union_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="boolean_difference_mesh_mesh", requires=["compas_cgal"])
def boolean_difference_mesh_mesh(A: Tessellation, B: Tessellation) -> Tessellation:
    from compas_cgal.booleans import boolean_difference_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="boolean_intersection_mesh_mesh", requires=["compas_cgal"])
def boolean_intersection_mesh_mesh(A: Tessellation, B: Tessellation) -> Tessellation:
    from compas_cgal.booleans import boolean_intersection_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="split_mesh_mesh", requires=["compas_cgal"])
def split_mesh_mesh(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesNumpy:
    from compas_cgal.booleans import split_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["boolean_difference_mesh_mesh", "boolean_intersection_mesh_mesh", "boolean_union_mesh_mesh", "split_mesh_mesh"]
