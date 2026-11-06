from compas.geometry import Box
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas_viewer import Viewer

from compas_cgal.subdivision import mesh_subdivide_catmull_clark
from compas_cgal.subdivision import mesh_subdivide_loop
from compas_cgal.subdivision import mesh_subdivide_sqrt3

# ==============================================================================
# Input geometry
# ==============================================================================

box = Box.from_diagonal(([0, 0, 0], [1, 1, 1]))

V0, F0 = box.to_tessellation().to_vertices_and_triangles()

# ==============================================================================
# Compute
# ==============================================================================

V4, F4 = mesh_subdivide_catmull_clark((V0, F0), 3)
V5, F5 = mesh_subdivide_loop((V0, F0), 3)
V6, F6 = mesh_subdivide_sqrt3((V0, F0), 3)

S2 = Polyhedron(V0, F0)
S4 = Polyhedron(V4, F4)
S6 = Polyhedron(V5, F5)
S8 = Polyhedron(V6, F6)

S2.transform(Translation.from_vector([1, 0, 0]))
S4.transform(Translation.from_vector([2, 0, 0]))
S6.transform(Translation.from_vector([3, 0, 0]))
S8.transform(Translation.from_vector([4, 0, 0]))

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [3, 1, 0.5]
viewer.renderer.camera.position = [5, -2, 0.5]

viewer.scene.add(S2.to_mesh(), show_points=False)
viewer.scene.add(S4.to_mesh(), show_points=False)
viewer.scene.add(S6.to_mesh(), show_points=False)
viewer.scene.add(S8.to_mesh(), show_points=False)

viewer.show()
