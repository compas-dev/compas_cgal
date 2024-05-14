import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Translation
from compas_cgal.skeletonization import mesh_skeleton
from compas_cgal.subdivision import mesh_subdivide_sqrt3

# from compas_view2.objects import Collection
from compas_viewer import Viewer

FILE = Path(__file__).parent.parent.parent / "data" / "elephant.off"

Rx = Rotation.from_axis_and_angle([1, 0, 0], math.radians(60))
Ry = Rotation.from_axis_and_angle([0, 1, 0], math.radians(5))
R = Ry * Rx
S = Scale.from_factors([5, 5, 5])
T = Translation.from_vector([0, 0, 2])
mesh = Mesh.from_off(FILE).transformed(T * R * S)

V, F = mesh.to_vertices_and_faces()
V, F = mesh_subdivide_sqrt3((V, F), k=2)

pointsets = mesh_skeleton((V, F))

polylines = []
for points in pointsets:
    polyline = Polyline(points)
    polylines.append(polyline)

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer(width=1600, height=900)

viewer.renderer.camera.target = [0, 0, 1.5]
viewer.renderer.camera.position = [-5, -5, 1.5]

viewer.scene.add(mesh, opacity=0.5, show_points=False)

for polyline in polylines:
    viewer.scene.add(polyline, lineswidth=5, show_points=False)

viewer.show()
