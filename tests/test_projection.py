from pathlib import Path
from compas.datastructures import Mesh
from compas_cgal.meshing import mesh_project


def mesh_projection():
    # Mesh to project
    input_file_0 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
    mesh_0 = Mesh.from_ply(input_file_0)

    # Target Mesh to project onto
    input_file_1 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_1.ply"
    mesh_1 = Mesh.from_ply(input_file_1)

    mesh_result = mesh_project(mesh_0, mesh_1, use_normals=False)

    assert mesh_result.number_of_vertices() == mesh_0.number_of_vertices()
