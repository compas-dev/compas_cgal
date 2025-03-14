from compas.geometry import Box
from compas.geometry import Polyhedron
from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas_cgal.booleans import (
    boolean_difference_mesh_mesh,
    boolean_intersection_mesh_mesh,
    boolean_union_mesh_mesh,
    split_mesh_mesh,
)
from compas_cgal.meshing import mesh_remesh
from compas_viewer import Viewer
from compas.geometry import Translation
from line_profiler import profile


def input():
    """Create an input for the boolean methods."""
    box = Box(2)
    A = box.to_vertices_and_faces(triangulated=True)
    sphere = Sphere(1, point=[1, 1, 1])
    B = sphere.to_vertices_and_faces(u=64, v=64, triangulated=True)
    B = mesh_remesh(B, 0.3, 50)
    return A, B


def boolean_difference():
    """Compute the boolean difference of two triangle meshes."""
    A, B = input()
    V, F = boolean_difference_mesh_mesh(A, B)
    shape = Polyhedron(V.tolist(), F.tolist())
    shape = shape.to_mesh()

    return shape


def boolean_intersection():
    """Compute the boolean intersection of two triangle meshes."""
    A, B = input()
    V, F = boolean_intersection_mesh_mesh(A, B)
    shape = Polyhedron(V.tolist(), F.tolist())
    shape = shape.to_mesh()

    return shape


def boolean_union():
    """Compute the boolean union of two triangle meshes."""
    A, B = input()
    V, F = boolean_union_mesh_mesh(A, B)
    shape = Polyhedron(V.tolist(), F.tolist())
    shape = shape.to_mesh()

    return shape


def split():
    """Compute the mesh split of two triangle meshes."""
    A, B = input()
    V, F = split_mesh_mesh(A, B)
    mesh = Mesh.from_vertices_and_faces(V, F)
    return mesh.exploded()


@profile
def main():
    """Compute the boolean difference, intersection, union, and split of two triangle meshes."""
    difference = boolean_difference()
    intersection = boolean_intersection()
    union = boolean_union()
    splits = split()
    return difference, intersection, union, splits


difference, intersection, union, splits = main()


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

difference.transform(Translation.from_vector([-6, 0, 0]))
intersection.transform(Translation.from_vector([-2, 0, 0]))
union.transform(Translation.from_vector([2, 0, 0]))
for m in splits:
    m.transform(Translation.from_vector([6, 0, 0]))

viewer.scene.add(difference, lineswidth=1, show_points=False)
viewer.scene.add(intersection, lineswidth=1, show_points=False)
viewer.scene.add(union, lineswidth=1, show_points=False)
viewer.scene.add(splits, lineswidth=1, show_points=False)

viewer.show()
