import numpy as np
import math
import compas

from compas.geometry import scale_vector
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Box
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Translation
from compas.geometry import Scale
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles

from compas_viewers.objectviewer import ObjectViewer

from compas_cgal.slicer import slice_mesh


# get the bunny
# and construct a mesh
# (this should be handled by TriMesh in the future)
mesh = Mesh.from_ply(compas.get('bunny.ply'))

# move the bunny to the origin
# and rotate it upright
vector = scale_vector(mesh.centroid(), -1)
T = Translation.from_vector(vector)
S = Scale.from_factors([100, 100, 100])
R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))
mesh.transform(R * S * T)

# create planes
bbox = mesh.bounding_box()
x, y, z = zip(*bbox)
xmin, xmax = min(x), max(x)
normal = Vector(1, 0, 0)
planes = []
for i in np.linspace(xmin, xmax, 100):
    plane = Plane(Point(i, 0, 0), normal)
    planes.append(plane)

# slice
pointsets = slice_mesh(
    mesh.to_vertices_and_faces(),
    planes)

# process output
polylines = []
for points in pointsets:
    points = [Point(*point) for point in points]  # otherwise Polygon throws an error
    polyline = Polyline(points)
    polylines.append(polyline)

# visualize
viewer = ObjectViewer()
viewer.view.use_shaders = False

for polyline in polylines:
    viewer.add(polyline, settings={'color': '#0000ff'})

viewer.update()
viewer.show()
