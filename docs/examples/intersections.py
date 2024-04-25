from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas_cgal.intersections import intersection_mesh_mesh
from compas_viewer import Viewer

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

viewer = Viewer()

# viewer.ui.window.viewport.view3d.camera.position = [...]
# viewer.ui.window.viewport.view3d.camera.target = [...]

viewer.scene.add(Mesh.from_vertices_and_faces(*A), facecolor=(1.0, 0.0, 0.0), show_points=False)
viewer.scene.add(Mesh.from_vertices_and_faces(*B), facecolor=(0.0, 1.0, 0.0), show_points=False, opacity=0.3)

for polyline in polylines:
    viewer.scene.add(
        polyline,
        linecolor=(0.0, 0.0, 1.0),
        linewidth=3,
        pointcolor=(0.0, 0.0, 1.0),
        pointsize=20,
        show_points=True,
    )

viewer.show()
