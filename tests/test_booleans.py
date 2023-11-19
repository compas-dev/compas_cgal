from compas.geometry import Box
from compas.geometry import Sphere
from compas.datastructures import Mesh

from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.meshing import mesh_remesh


def test_booleans():
    # ==============================================================================
    # Make a box and a sphere
    # ==============================================================================

    box = Box(2)
    A = box.to_vertices_and_faces(triangulated=True)

    sphere = Sphere(1, point=[1, 1, 1])
    B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    # ==============================================================================
    # Remesh the sphere
    # ==============================================================================

    B = mesh_remesh(B, 0.3, 10)

    # ==============================================================================
    # Compute the boolean mesh
    # ==============================================================================

    V, F = boolean_union_mesh_mesh(A, B)

    Mesh.from_vertices_and_faces(V, F)
