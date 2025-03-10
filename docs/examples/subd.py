from compas.geometry import Box
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas_cgal.subdivision import mesh_subdivide_sqrt3 as mesh_subdivide
from compas_viewer import Viewer

# ==============================================================================
# Input
# ==============================================================================

box = Box.from_diagonal(([0, 0, 0], [1, 1, 1]))

V, F = box.to_vertices_and_faces(triangulated=True)

V2, F2 = mesh_subdivide((V, F), 2)
V4, F4 = mesh_subdivide((V, F), 4)
V6, F6 = mesh_subdivide((V, F), 6)
V8, F8 = mesh_subdivide((V, F), 8)

S2 = Polyhedron(V2.tolist(), F2.tolist())
S4 = Polyhedron(V4.tolist(), F4.tolist())
S6 = Polyhedron(V6.tolist(), F6.tolist())
S8 = Polyhedron(V8.tolist(), F8.tolist())

S2.transform(Translation.from_vector([1, 0, 0]))
S4.transform(Translation.from_vector([2, 0, 0]))
S6.transform(Translation.from_vector([3, 0, 0]))
S8.transform(Translation.from_vector([4, 0, 0]))

# ==============================================================================
# Viz
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [3, 1, 0.5]
viewer.renderer.camera.position = [5, -2, 0.5]

viewer.scene.add(box.to_mesh(), show_points=False)
viewer.scene.add(S2.to_mesh(), show_points=False)
viewer.scene.add(S4.to_mesh(), show_points=False)
viewer.scene.add(S6.to_mesh(), show_points=False)
viewer.scene.add(S8.to_mesh(), show_points=False)

viewer.show()
