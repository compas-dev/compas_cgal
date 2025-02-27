from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_viewer import Viewer

from compas_cgal.reconstruction import pointset_reduction

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
reduced = Pointcloud(points)

# Result
print(f"Original points: {len(cloud)}, Reduced points: {len(reduced)}")

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0.5, 0]
viewer.renderer.camera.position = [0, -1, 2]

cloud.scale(1e-3)
cloud.translate([-cloud.aabb.xmax - 0.1 * cloud.aabb.xsize, 0, 0])

reduced.scale(1e-3)
reduced.translate([-reduced.aabb.xmin + 0.1 * reduced.aabb.xsize, 0, 0])

viewer.scene.add(cloud, name="Original")
viewer.scene.add(reduced, name="Reduced")

viewer.show()
