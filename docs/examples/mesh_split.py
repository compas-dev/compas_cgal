from compas.geometry import Box, Sphere
from compas.datastructures import Mesh
from compas.colors import Color
from compas_view2.app import App

from compas_cgal.booleans import split_mesh_mesh

# ==============================================================================
# Make a box and a sphere
# ==============================================================================

box = Box(2)
A = box.to_vertices_and_faces(triangulated=True)

sphere = Sphere(1, point=[1, 1, 1])
B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

# ==============================================================================
# Compute the mesh split
# ==============================================================================

V, F = split_mesh_mesh(A, B)

mesh = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Seperate disjoint faces and visualize
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -4, 2]
viewer.view.camera.look_at([0, 0, 0])

for color, vertices in zip([Color.blue(), Color.pink()], mesh.connected_components()):
    faces = []
    for indices in F:
        if all(index in vertices for index in indices):
            faces.append(indices)
    mesh = Mesh.from_vertices_and_faces(V, faces)
    mesh.remove_unused_vertices()
    viewer.add(mesh, facecolor=color)

viewer.run()
