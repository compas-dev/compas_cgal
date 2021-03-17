from compas.geometry import boolean_union_mesh_mesh
from compas.geometry import Box
from compas.datastructures import Mesh
from compas.geometry import Frame
from compas_view2.app import App

b1 = Box(Frame([+4, +4, 0], [1, 0, 0], [0, 1, 0]), 10, 10, 10)
b2 = Box(Frame([-4, -4, 0], [1, 0, 0], [0, 1, 0]), 10, 10, 10)

a = Mesh.from_shape(b1)
b = Mesh.from_shape(b2)
a.quads_to_triangles()
b.quads_to_triangles()
A = a.to_vertices_and_faces()
B = b.to_vertices_and_faces()

V, F = boolean_union_mesh_mesh(A, B)

c = Mesh.from_vertices_and_faces(V, F)
print(c.summary())

viewer = App()
viewer.add(a, show_faces=False)
viewer.add(b, show_faces=False)
viewer.add(c)
viewer.run()
