from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import intersection_mesh_mesh
from compas_viewer import Viewer

# ==============================================================================
# Make a box and a sphere
# ==============================================================================

box = Box(2)
A = box.to_tessellation().to_vertices_and_triangles()

sphere = Sphere(1, frame=Frame(point=[1, 1, 1]))
B = sphere.to_tessellation(nu=32, nv=32).to_vertices_and_triangles()

# ==============================================================================
# Compute the intersections
# ==============================================================================

pointsets = intersection_mesh_mesh(A, B)

# ==============================================================================
# Process output
# ==============================================================================

polylines = []
for points in pointsets:
    points = [Point(point[0], point[1], point[2]) for point in points]
    polyline = Polyline(points)
    polylines.append(polyline)

# =============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [4, -6, 3]

viewer.scene.add(
    box,
    facecolor=(1.0, 0.0, 0.0),
    show_points=False,
)

viewer.scene.add(
    sphere,
    facecolor=(0.0, 1.0, 0.0),
    show_points=False,
    opacity=0.3,
)

for polyline in polylines:
    viewer.scene.add(
        polyline,
        linecolor=(0.0, 0.0, 1.0),
        lineswidth=3,
        pointcolor=(0.0, 0.0, 1.0),
        pointsize=20,
        show_points=True,
    )

viewer.show()
