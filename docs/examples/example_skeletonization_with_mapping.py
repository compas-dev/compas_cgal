import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Translation
from compas_viewer import Viewer

from compas_cgal.skeletonization import mesh_skeleton_with_mapping

# =============================================================================
# Input
# =============================================================================

input_file = Path(__file__).parent.parent.parent / "data" / "elephant.off"

R1 = Rotation.from_axis_and_angle([1, 0, 0], math.radians(60))
R2 = Rotation.from_axis_and_angle([0, 1, 0], math.radians(5))
T = Translation.from_vector([0, 0, 2])
S = Scale.from_factors([5, 5, 5])

transform = T * R2 * R1 * S

mesh = Mesh.from_off(input_file).transformed(transform)
v, f = mesh.to_vertices_and_faces(triangulated=True)

# =============================================================================
# Compute skeleton with vertex mapping
# =============================================================================

skeleton_edges, vertex_indices = mesh_skeleton_with_mapping((v, f))

# Create polylines for skeleton edges

polylines = [Polyline([start, end]) for start, end in skeleton_edges]

# Select edge to highlight (100th or last if fewer edges)

edge_idx = min(100, len(vertex_indices) - 1)
start_indices, end_indices = vertex_indices[edge_idx]

print(f"Mesh: {len(v)} vertices, Skeleton: {len(skeleton_edges)} edges")
print(f"Edge {edge_idx}: {len(start_indices)} vertices → start, {len(end_indices)} vertices → end")

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 1.5]
viewer.renderer.camera.position = [-5, -5, 1.5]

viewer.scene.add(mesh, opacity=0.2, show_points=False, facecolor=[0.9, 0.9, 0.9])

for idx in start_indices:
    viewer.scene.add(Point(*v[idx]), pointcolor=[1.0, 0.0, 0.0], pointsize=15)  # red = start
for idx in end_indices:
    viewer.scene.add(Point(*v[idx]), pointcolor=[0.0, 0.0, 1.0], pointsize=15)  # blue = end

for i, polyline in enumerate(polylines):
    if i == edge_idx:
        viewer.scene.add(
            polyline,
            linewidth=10,
            linecolor=[1.0, 1.0, 0.0],
            show_points=True,
            pointsize=20,
        )
    else:
        viewer.scene.add(
            polyline,
            linewidth=3,
            linecolor=[0.5, 0.5, 0.5],
            show_points=False,
        )

viewer.show()
