from compas_cgal import booleans

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Box
from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles
from compas.datastructures import mesh_subdivide_quad
from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject

R = 1.4

O = Point(0, 0, 0)
X = Vector(1, 0, 0)
Y = Vector(0, 1, 0)
Z = Vector(0, 0, 1)
YZ = Plane(O, X)
ZX = Plane(O, Y)
XY = Plane(O, Z)

box = Box.from_width_height_depth(2 * R, 2 * R, 2 * R)
box = Mesh.from_shape(box)
box = mesh_subdivide_quad(box, k=1)
mesh_quads_to_triangles(box)

sphere = Sphere(O, 1.25 * R)
sphere = Mesh.from_shape(sphere, u=50, v=50)
mesh_quads_to_triangles(sphere)

# mesh = booleans.boolean_union(box, sphere, False)
# mesh = booleans.boolean_difference(box, sphere)
mesh = booleans.boolean_intersection(box, sphere, False)

meshes = []
meshes.append(MeshObject(mesh, color='#cccccc'))

viewer = MultiMeshViewer()
viewer.meshes = meshes

viewer.show()
