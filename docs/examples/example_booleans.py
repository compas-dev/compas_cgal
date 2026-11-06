from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.geometry import boolean_difference_mesh_mesh
from compas.geometry import boolean_intersection_mesh_mesh
from compas.geometry import boolean_union_mesh_mesh
from compas_viewer import Viewer

# =============================================================================
# Input
# =============================================================================

box = Box(2)
A = box.to_tessellation().to_vertices_and_triangles()
sphere = Sphere(1, frame=Frame(point=[1, 1, 1]))
B = sphere.to_tessellation(nu=64, nv=64).to_vertices_and_triangles()


# =============================================================================
# Booleans
# =============================================================================

difference = Mesh.from_vertices_and_faces(*boolean_difference_mesh_mesh(A, B))
intersection = Mesh.from_vertices_and_faces(*boolean_intersection_mesh_mesh(A, B))
union = Mesh.from_vertices_and_faces(*boolean_union_mesh_mesh(A, B))

# =============================================================================
# Spread
# =============================================================================

difference.transform(Translation.from_vector([-6, 0, 0]))
intersection.transform(Translation.from_vector([-2, 0, 0]))
union.transform(Translation.from_vector([2, 0, 0]))


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.scene.add(difference, lineswidth=1, show_points=False)
viewer.scene.add(intersection, lineswidth=1, show_points=False)
viewer.scene.add(union, lineswidth=1, show_points=False)

viewer.show()
