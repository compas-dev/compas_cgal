"""Mesh plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas_cgal.types import PolylinesNumpySkeleton
    from compas_cgal.types import SkeletonVertexMapping
    from compas_cgal.types import VerticesFaces


@plugin(category="mesh", requires=["compas_cgal"])
def mesh_skeleton(mesh: VerticesFaces) -> PolylinesNumpySkeleton:
    from compas_cgal.skeletonization import mesh_skeleton as implementation

    return implementation(mesh)


@plugin(category="mesh", requires=["compas_cgal"])
def mesh_skeleton_with_mapping(mesh: VerticesFaces) -> tuple[PolylinesNumpySkeleton, SkeletonVertexMapping]:
    from compas_cgal.skeletonization import mesh_skeleton_with_mapping as implementation

    return implementation(mesh)


__all__ = ["mesh_skeleton", "mesh_skeleton_with_mapping"]
