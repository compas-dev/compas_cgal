from pathlib import Path

from compas.colors import Color
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Pointcloud
from compas_viewer import Viewer

from compas_cgal.reconstruction import pointset_normal_estimation

# Define the file path for the point cloud data
FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"

# Load the point cloud data from the PLY file
cloud = Pointcloud.from_ply(FILE)

# Estimate normals for the point cloud
points, vectors = pointset_normal_estimation(cloud, 16, True)
print(f"Original points: {len(cloud)}, Points with normals: {len(points)}, Vectors: {len(vectors)}")

cloud = Pointcloud(points)
cloud.scale(1e-3)

# =============================================================================
# Pre-prcessing
# =============================================================================

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

viewer.show()
