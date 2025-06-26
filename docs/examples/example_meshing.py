from pathlib import Path
from compas.datastructures import Mesh
from compas_viewer import Viewer

from compas_cgal.meshing import trimesh_remesh


input_file = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
mesh = Mesh.from_ply(input_file)
mesh.quads_to_triangles()

edge_length = 1
iterations = 10

# Remesh
V1, F1 = trimesh_remesh(mesh.to_vertices_and_faces(), edge_length, iterations)
remeshed = Mesh.from_vertices_and_faces(V1, F1)


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.25, 0.10]

viewer.scene.add(mesh, show_points=False, opacity=0.25)
viewer.scene.add(remeshed, show_points=True)

viewer.show()
