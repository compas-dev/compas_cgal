from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_cgal.reconstruction import pointset_smoothing
from compas_viewer import Viewer

# Define the path to the PLY file
ply_file_path = Path(__file__).parent.parent.parent / "data" / "box.ply"

# Load the original point cloud and translate it
original_points = Pointcloud.from_ply(ply_file_path)
original_points.transform(Translation.from_vector([-10000, 0, 0]))

# Load another copy of the point cloud for comparison and translate it in the opposite direction
transformed_points = Pointcloud.from_ply(ply_file_path)
transformed_points.transform(Translation.from_vector([10000, 0, 0]))

# Apply point set smoothing to the transformed point cloud
smoothed_points = pointset_smoothing(transformed_points, 1000, 3)

# Create Pointcloud objects for visualization
cloud_original = Pointcloud(original_points)
cloud_transformed = Pointcloud(smoothed_points)

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

# viewer.view.camera.scale = 1000
# viewer.view.grid.cell_size = 1000

# viewer.scene.add(cloud_original)
# viewer.scene.add(cloud_transformed)

# viewer.view.camera.zoom_extents()

viewer.show()
