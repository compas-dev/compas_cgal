import math
import compas

from compas.geometry import scale_vector
from compas.geometry import Vector
from compas.geometry import Rotation
from compas.geometry import Translation
from compas.geometry import Scale
from compas.datastructures import Mesh

from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject

from compas_cgal.meshing import remesh


# ==============================================================================
# Get the bunny and construct a mesh
# ==============================================================================

bunny = Mesh.from_ply(compas.get('bunny.ply'))

bunny.cull_vertices()

# ==============================================================================
# Move the bunny to the origin and rotate it upright.
# ==============================================================================

vector = scale_vector(bunny.centroid(), -1)
T = Translation.from_vector(vector)
S = Scale.from_factors([100, 100, 100])
R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

bunny.transform(R * S * T)

# ==============================================================================
# Remesh
# ==============================================================================

num_edges = bunny.number_of_edges()
length = sum(bunny.edge_length(*edge) for edge in bunny.edges()) / num_edges

V, F = remesh(bunny.to_vertices_and_faces(), 2 * length, 10)

bunny = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Visualize
# ==============================================================================

meshes = []
meshes.append(MeshObject(bunny, color='#cccccc'))

viewer = MultiMeshViewer()
viewer.meshes = meshes

viewer.show()
