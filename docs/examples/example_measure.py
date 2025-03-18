from compas.datastructures import Mesh
from compas.geometry import Box
from line_profiler import profile

from compas_cgal.measure import mesh_area
from compas_cgal.measure import mesh_centroid
from compas_cgal.measure import mesh_volume


@profile
def main(mesh):
    """Mesh measurement methods."""
    area = mesh_area(mesh)
    volume = mesh_volume(mesh)
    centroid = mesh_centroid(mesh)
    return area, volume, centroid


# ==============================================================================
# Input geometry
# ==============================================================================

box = Box(1)
v, f = box.to_vertices_and_faces()
mesh = Mesh.from_vertices_and_faces(v, f)
mesh.quads_to_triangles()
V, F = mesh.to_vertices_and_faces()


# ==============================================================================
# Compute
# ==============================================================================

result = main((V, F))

print("Area:", result[0])
print("Volume:", result[1])
print("Centroid:", result[2])
