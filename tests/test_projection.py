from pathlib import Path
from compas.datastructures import Mesh
from compas_cgal.meshing import project_mesh_on_mesh, pull_mesh_on_mesh


def mesh_projection():
    # Mesh to project
    input_file_0 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
    mesh_0 = Mesh.from_ply(input_file_0)

    # Target Mesh to project onto
    input_file_1 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_1.ply"
    mesh_1 = Mesh.from_ply(input_file_1)

    mesh_result = project_mesh_on_mesh(mesh_0, mesh_1)
    assert mesh_result.number_of_vertices() == mesh_0.number_of_vertices()

    mesh_result = pull_mesh_on_mesh(mesh_0, mesh_1)
    assert mesh_result.number_of_vertices() == mesh_0.number_of_vertices()
