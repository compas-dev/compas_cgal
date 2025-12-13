from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Point
from compas_viewer import Viewer

from compas_cgal.meshing import project_mesh_on_mesh
from compas_cgal.meshing import project_points_on_mesh
from compas_cgal.meshing import pull_mesh_on_mesh
from compas_cgal.meshing import pull_points_on_mesh

# =============================================================================
# Source
# =============================================================================

input_file_0 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
mesh_0 = Mesh.from_ply(input_file_0)

# =============================================================================
# Target
# =============================================================================

input_file_1 = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_1.ply"
mesh_1 = Mesh.from_ply(input_file_1)

# =============================================================================
# Source vertices and normals
# =============================================================================

v, f = mesh_0.to_vertices_and_faces()
normals = []
for i in range(len(v)):
    normals.append(mesh_0.vertex_normal(i))

# =============================================================================
# Projection
# =============================================================================

mesh_result_project = project_mesh_on_mesh(mesh_0, mesh_1)
points_result_project = project_points_on_mesh(v, mesh_1)

# =============================================================================
# Pulling
# =============================================================================

mesh_result_pull = pull_mesh_on_mesh(mesh_0, mesh_1)
points_result_pull = pull_points_on_mesh(v, normals, mesh_1)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()
viewer.renderer.camera.target = [0, 0, 1.5]
viewer.renderer.camera.position = [-5, -5, 1.5]

viewer.scene.add(mesh_0, name="source mesh_0", show_faces=False)
viewer.scene.add(mesh_1, name="target mesh_1", show_faces=False)

viewer.scene.add(mesh_result_project, name="projected mesh", color=[255, 0, 0])
viewer.scene.add(mesh_result_pull, name="pulled mesh", color=[0, 255, 0])

group_projected = viewer.scene.add_group("projected points")
for i, point in enumerate(points_result_project):
    group_projected.add(Point(*point), name=f"point_{i}", color=[0, 0, 0])

group_pulled = viewer.scene.add_group("pulled points")
for i, point in enumerate(points_result_pull):
    group_pulled.add(Point(*point), name=f"point_{i}", color=[0, 0, 0])

viewer.show()
