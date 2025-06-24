from pathlib import Path

from compas.datastructures import Mesh
from compas_viewer import Viewer

from compas_cgal.meshing import mesh_project


# Mesh to project
input_file_0 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
mesh_0 = Mesh.from_ply(input_file_0)

# Target Mesh to project onto
input_file_1 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_1.ply"
mesh_1 = Mesh.from_ply(input_file_1)

mesh_result = mesh_project(mesh_0, mesh_1, use_normals=False)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()
viewer.renderer.camera.target = [0, 0, 1.5]
viewer.renderer.camera.position = [-5, -5, 1.5]

viewer.scene.add(mesh_0, name="source mesh_0", show_faces=False)
viewer.scene.add(mesh_1, name="target mesh_1", show_faces=False)
viewer.scene.add(mesh_result, name="projected mesh_result", color=[255, 0, 0])

viewer.show()
