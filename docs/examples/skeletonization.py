import math
from pathlib import Path
from compas.datastructures import Mesh
from compas.geometry import Polyline
from compas.geometry import Rotation, Scale, Translation
from compas_view2.app import App
from compas_view2.objects import Collection
from compas_cgal.skeletonization import mesh_skeleton
from compas_cgal.subdivision import mesh_subdivide_sqrt3

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

viewer = App(width=1600, height=900)
viewer.view.camera.position = [-5, -5, 1.5]
viewer.view.camera.look_at([0, 0, 1.5])

viewer.add(mesh, opacity=0.5)
viewer.add(Collection(polylines), linewidth=5)
viewer.run()
