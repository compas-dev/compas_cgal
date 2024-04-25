from compas.geometry import Box
from compas.geometry import Polyhedron
from compas.geometry import Sphere
from compas_cgal.booleans import boolean_union_mesh_mesh
from compas_cgal.meshing import mesh_remesh
from compas_viewer import Viewer

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

# temp solution until viewer supports polyhedrons
shape = shape.to_mesh()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

# viewer.ui.window.viewport.view3d.camera.position = [...]
# viewer.ui.window.viewport.view3d.camera.target = [...]

viewer.scene.add(shape, linewidth=2, show_points=False)
viewer.show()
