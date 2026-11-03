from compas.geometry import Box
from compas.geometry import Native
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import UVGrid
from compas.geometry import intersection_mesh_mesh
from compas_viewer import Viewer

# ==============================================================================
# Make a box and a sphere
# ==============================================================================

box = Box(2)
A = box.tessellate(Native())

sphere = Sphere(1, point=[1, 1, 1])
B = sphere.tessellate(UVGrid(32, 32))

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

# =============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [4, -6, 3]

viewer.scene.add(
    A.to_mesh(),
    facecolor=(1.0, 0.0, 0.0),
    show_points=False,
)

viewer.scene.add(
    B.to_mesh(),
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
