from pathlib import Path

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_cgal.reconstruction import pointset_reduction
from compas_viewer import Viewer

# Define the file path for the point cloud data
FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"

# Load the original point cloud
original_points = Pointcloud.from_ply(FILE)

# Create a copy of the point cloud for processing
cloud = Pointcloud.from_ply(FILE)

# Translate the original point cloud
cloud.transform(Translation.from_vector([-1000, 0, 0]))

# Apply point set reduction to the translated point cloud
points = pointset_reduction(cloud, 50)
print(f"Original points: {len(cloud)}, Reduced points: {len(points)}")

# =============================================================================
# Viz
# =============================================================================

# Initialize the COMPAS viewer
viewer = Viewer()

# viewer.ui.window.viewport.view3d.camera.position = [...]
# viewer.ui.window.viewport.view3d.camera.target = [...]

# viewer.scene.add(Pointcloud(points))
# viewer.scene.add(Pointcloud(original_points))

for x, y, z in points:
    viewer.scene.add(Point(x, y, z).scaled(1e-3, 1e-3, 1e-3))

# viewer.view.camera.zoom_extents()

viewer.show()
