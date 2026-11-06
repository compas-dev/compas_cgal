"""Triangle-mesh plugin registrations for COMPAS."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry._typing import PlaneType
    from compas.typing import VerticesFaces

    from compas_cgal.types import PolylinesNumpy
    from compas_cgal.types import VerticesFacesNumpy


@plugin(category="trimesh", pluggable_name="_trimesh_remesh", requires=["compas_cgal._meshing"])
def _trimesh_remesh(
    mesh: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
) -> VerticesFacesNumpy:
    from compas_cgal.meshing import trimesh_remesh as implementation

    return implementation(
        mesh,
        target_edge_length,
        number_of_iterations,
        do_project,
    )


@plugin(category="trimesh", pluggable_name="_trimesh_slice", requires=["compas_cgal._slicer"])
def _trimesh_slice(mesh: VerticesFaces, planes: Sequence[PlaneType]) -> PolylinesNumpy:
    from compas_cgal.slicer import slice_mesh_planes as implementation

    return implementation(mesh, planes)


__all__ = ["_trimesh_remesh", "_trimesh_slice"]
