from compas.datastructures import Mesh
from compas.geometry import Box

from compas_cgal.measure import mesh_area
from compas_cgal.measure import mesh_centroid
from compas_cgal.measure import mesh_volume

# ==============================================================================
# Input geometry
# ==============================================================================

box = Box(1)
v, f = box.to_vertices_and_faces()
mesh = Mesh.from_vertices_and_faces(v, f)
mesh.quads_to_triangles()
VF = mesh.to_vertices_and_faces()

# ==============================================================================
# Compute
# ==============================================================================

area = mesh_area(VF)
volume = mesh_volume(VF)
centroid = mesh_centroid(VF)


print("Area:", area)
print("Volume:", volume)
print("Centroid:", centroid)
