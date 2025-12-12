from pathlib import Path

from compas.datastructures import Mesh
from compas_viewer import Viewer

from compas_cgal.meshing import trimesh_remesh

# =============================================================================
# Input mesh
# =============================================================================

input_file = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"

mesh = Mesh.from_ply(input_file)
mesh.quads_to_triangles()

VF = mesh.to_vertices_and_faces()

# =============================================================================
# Remesh
# =============================================================================

V1, F1 = trimesh_remesh(VF, target_edge_length=1, number_of_iterations=10)

remeshed = Mesh.from_vertices_and_faces(V1, F1)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.scene.add(mesh, show_points=False, opacity=0.25)
viewer.scene.add(remeshed, show_points=True)

viewer.show()
