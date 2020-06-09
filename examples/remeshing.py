import os
import math
import time

from compas.geometry import scale_vector
from compas.geometry import Vector
from compas.geometry import Rotation
from compas.geometry import Translation
from compas.geometry import Scale
from compas.utilities import pairwise

from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject

from compas_cgal.trimesh import TriMesh

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '..', 'data', 'Bunny.ply')
SPLITS = []

SPLITS.append(time.time())

# ==============================================================================
# Get the bunny and construct a mesh
# ==============================================================================

bunny = TriMesh.from_ply(FILE)

SPLITS.append(time.time())

bunny.cull_vertices()

SPLITS.append(time.time())

# ==============================================================================
# Move the bunny to the origin and rotate it upright.
# ==============================================================================

vector = scale_vector(bunny.centroid, -1)

T = Translation.from_vector(vector)
S = Scale.from_factors([100, 100, 100])
R = Rotation.from_axis_and_angle(Vector(1, 0, 0), math.radians(90))

bunny.transform(R * S * T)

SPLITS.append(time.time())

# ==============================================================================
# Remesh
# ==============================================================================

length = bunny.average_edge_length

SPLITS.append(time.time())

bunny.remesh(3 * length)

SPLITS.append(time.time())

mesh = bunny.to_mesh()

SPLITS.append(time.time())

# ==============================================================================
# Visualize
# ==============================================================================

processes = ['bunny', 'cull', 'transform', 'length', 'remesh', 'mesh']
times = [t2 - t1 for t1, t2 in pairwise(SPLITS)]

for name, t in zip(processes, times):
    print(f"{name}: {t:.4f}")

meshes = []
meshes.append(MeshObject(mesh, color='#cccccc'))

viewer = MultiMeshViewer()
viewer.meshes = meshes

viewer.show()
