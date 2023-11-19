from compas.geometry import Point
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Polyline
from compas.datastructures import Mesh

from compas_view2.app import App

from compas_cgal.intersections import intersection_mesh_mesh

# ==============================================================================
# Make a box and a sphere
# ==============================================================================

box = Box(2)
A = box.to_vertices_and_faces(triangulated=True)

sphere = Sphere(1, point=[1, 1, 1])
B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

# ==============================================================================
# Compute the intersections
# ==============================================================================

pointsets = intersection_mesh_mesh(A, B)

# ==============================================================================
# Process output
# ==============================================================================

polylines = []
for points in pointsets:
    points = [Point(*point) for point in points]
    polyline = Polyline(points)
    polylines.append(polyline)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -4, 2]
viewer.view.camera.look_at([0, 1, 0])

viewer.add(Mesh.from_vertices_and_faces(*A), facecolor=(1, 0, 0), opacity=0.3)
viewer.add(Mesh.from_vertices_and_faces(*B), facecolor=(0, 1, 0), opacity=0.3)

for polyline in polylines:
    viewer.add(
        polyline,
        linecolor=(0, 0, 1),
        linewidth=3,
        pointcolor=(0, 0, 1),
        pointsize=20,
        show_points=True,
    )

viewer.show()
