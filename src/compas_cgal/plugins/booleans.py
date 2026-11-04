"""Boolean plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas._typing import TriangleMeshInput

    from compas_cgal.types import VerticesFaces
    from compas_cgal.types import VerticesFacesNumpy


@plugin(category="booleans", pluggable_name="_boolean_union_mesh_mesh", requires=["compas_cgal"])
def _boolean_union_mesh_mesh(A: TriangleMeshInput, B: TriangleMeshInput) -> TriangleMeshInput:
    from compas_cgal.booleans import boolean_union_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="_boolean_difference_mesh_mesh", requires=["compas_cgal"])
def _boolean_difference_mesh_mesh(A: TriangleMeshInput, B: TriangleMeshInput) -> TriangleMeshInput:
    from compas_cgal.booleans import boolean_difference_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="_boolean_intersection_mesh_mesh", requires=["compas_cgal"])
def _boolean_intersection_mesh_mesh(A: TriangleMeshInput, B: TriangleMeshInput) -> TriangleMeshInput:
    from compas_cgal.booleans import boolean_intersection_mesh_mesh as implementation

    return implementation(A, B)


@plugin(category="booleans", pluggable_name="split_mesh_mesh", requires=["compas_cgal"])
def split_mesh_mesh(A: VerticesFaces, B: VerticesFaces) -> VerticesFacesNumpy:
    from compas_cgal.booleans import split_mesh_mesh as implementation

    return implementation(A, B)


__all__ = ["_boolean_difference_mesh_mesh", "_boolean_intersection_mesh_mesh", "_boolean_union_mesh_mesh", "split_mesh_mesh"]
