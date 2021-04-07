from compas.geometry import Box, Frame
from compas.datastructures import Mesh

from compas_cgal.measure import volume

box = Box(Frame.worldXY(), 1, 1, 1)

mesh = Mesh.from_shape(box)
mesh.quads_to_triangles()

V = volume(mesh.to_vertices_and_faces())

print(V)
