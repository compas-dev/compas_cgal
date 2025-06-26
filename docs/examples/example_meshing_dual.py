from pathlib import Path
from compas.geometry import Line
from compas.datastructures import Mesh
from compas_viewer import Viewer

from compas_cgal.meshing import trimesh_dual


input_file = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"
mesh = Mesh.from_ply(input_file)
mesh.quads_to_triangles()


fixed_vertices = []
for v in mesh.vertices():
    if mesh.vertex_point(v).z < 0.01:
        fixed_vertices.append(v)

# Remesh and Dual
V2, F2, V3, F3 = trimesh_dual(mesh.to_vertices_and_faces(), length_factor=1.0, number_of_iterations=100, angle_radians=0.9, fixed_vertices=[])
remeshed, dual = Mesh.from_vertices_and_faces(V2, F2), Mesh.from_vertices_and_faces(V3, F3)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.25, 0.10]

viewer.scene.add(mesh, show_points=False, opacity=0.25)
remeshed.translate([0, 0, 3])
viewer.scene.add(remeshed, show_points=True)
viewer.scene.add(dual, show_points=True)

for v in dual.vertices():
    viewer.scene.add(Line(dual.vertex_point(v), dual.vertex_point(v)+dual.vertex_normal(v)*0.25), color=(255, 0, 0))

viewer.show()
