from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import DiagonalSplit
from compas.geometry import EarClipping
from compas.geometry import FaceTriangulation
from compas.geometry import trimesh_remesh
from compas_viewer import Viewer

# =============================================================================
# Input mesh
# =============================================================================

input_file = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"

mesh = Mesh.from_ply(input_file)
tessellation = mesh.triangulated(FaceTriangulation(quad=DiagonalSplit()))

# =============================================================================
# Remesh to a uniform target edge length
# =============================================================================

TARGET_EDGE_LENGTH = 1
ITERATIONS = 10

result = trimesh_remesh(tessellation, TARGET_EDGE_LENGTH, ITERATIONS)
remeshed = result.to_mesh()

# =============================================================================
# Visualize
# =============================================================================

viewer = Viewer()
viewer.scene.add(mesh, show_points=False, opacity=0.25)
viewer.scene.add(remeshed, show_points=True)

viewer.show()
