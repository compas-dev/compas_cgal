"""Triangle-mesh plugin registrations for COMPAS."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas._typing import CoordinatesCollectionInput
    from compas._typing import TriangleMeshInput
    from compas.geometry import Tessellation
    from compas.geometry._typing import PlaneType


@plugin(category="trimesh", pluggable_name="trimesh_remesh", requires=["compas_cgal"])
def trimesh_remesh(
    mesh: Tessellation,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
) -> Tessellation:
    from compas_cgal.meshing import trimesh_remesh as implementation

    return implementation(
        mesh,
        target_edge_length,
        number_of_iterations,
        do_project,
    )


@plugin(category="trimesh", pluggable_name="_trimesh_slice", requires=["compas_cgal"])
def _trimesh_slice(mesh: TriangleMeshInput, planes: Sequence[PlaneType]) -> CoordinatesCollectionInput:
    from compas_cgal.slicer import slice_mesh_planes as implementation

    return implementation(mesh, planes)


__all__ = ["_trimesh_slice", "trimesh_remesh"]
