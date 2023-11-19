from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Polyhedron

from compas_view2.app import App

from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.meshing import mesh_remesh

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

B = mesh_remesh(B, 0.3, 50)

# ==============================================================================
# Compute the boolean mesh
# ==============================================================================

V, F = boolean_union_mesh_mesh(A, B)
shape = Polyhedron(V.tolist(), F.tolist())  # revise the Shape API

# ==============================================================================
# Visualize
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -4, 2]
viewer.view.camera.look_at([0, 1, 0])

viewer.add(shape, linewidth=2)

viewer.run()
