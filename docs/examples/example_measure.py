from compas.geometry import Box
from compas.geometry import Native

from compas_cgal.measure import mesh_area
from compas_cgal.measure import mesh_centroid
from compas_cgal.measure import mesh_volume

# ==============================================================================
# Input geometry
# ==============================================================================

box = Box(1)
VF = box.tessellate(Native()).to_vertices_and_triangles()

# ==============================================================================
# Compute
# ==============================================================================

area = mesh_area(VF)
volume = mesh_volume(VF)
centroid = mesh_centroid(VF)


print("Area:", area)
print("Volume:", volume)
print("Centroid:", centroid)
