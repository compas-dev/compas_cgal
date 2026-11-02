"""Triangle-mesh plugin registrations for COMPAS."""

from __future__ import annotations

from typing import TYPE_CHECKING

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Plane

    from compas_cgal.types import PolylinesNumpy
    from compas_cgal.types import VerticesFaces
    from compas_cgal.types import VerticesFacesNumpy


@plugin(category="trimesh", pluggable_name="trimesh_volume", requires=["compas_cgal"])
def mesh_volume(mesh: VerticesFaces) -> float:
    from compas_cgal.measure import mesh_volume as implementation

    return implementation(mesh)


@plugin(category="trimesh", pluggable_name="trimesh_remesh", requires=["compas_cgal"])
def trimesh_remesh(
    mesh: VerticesFaces,
    target_edge_length: float,
    number_of_iterations: int = 10,
    do_project: bool = True,
    protect_boundary: bool = False,
    protect_sharp_edges_angle_deg: float = 0.0,
    keep_points=None,
) -> VerticesFacesNumpy:
    from compas_cgal.meshing import trimesh_remesh as implementation

    return implementation(
        mesh,
        target_edge_length,
        number_of_iterations,
        do_project,
        protect_boundary,
        protect_sharp_edges_angle_deg,
        keep_points,
    )


@plugin(category="trimesh", pluggable_name="trimesh_slice", requires=["compas_cgal"])
def slice_mesh_planes(mesh: VerticesFaces, planes: list[Plane]) -> PolylinesNumpy:
    from compas_cgal.slicer import slice_mesh_planes as implementation

    return implementation(mesh, planes)


__all__ = ["mesh_volume", "slice_mesh_planes", "trimesh_remesh"]
