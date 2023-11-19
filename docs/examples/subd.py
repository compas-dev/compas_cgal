from compas.geometry import Box, Polyhedron
from compas.geometry import Translation
from compas_cgal.subdivision import mesh_subdivide_sqrt3 as mesh_subdivide
from compas_view2.app import App

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

viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -2, 0.5]
viewer.view.camera.look_at([3, 1, 0.5])

viewer.add(box)
viewer.add(S2)
viewer.add(S4)
viewer.add(S6)
viewer.add(S8)
viewer.show()
