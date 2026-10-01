from pathlib import Path

from compas.geometry import Pointcloud
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.reconstruction import pointset_smoothing

# =============================================================================
# Input
# =============================================================================

ply_file_path = Path(__file__).parent.parent.parent / "data" / "box.ply"
original_points = Pointcloud.from_ply(ply_file_path)

# =============================================================================
# Smoothing
# =============================================================================

smoothed_points = Pointcloud(pointset_smoothing(original_points, 100, 3))

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.unit = "mm"

viewer = Viewer(config=config)
viewer.scene.add(original_points, pointcolor=(0.0, 0.0, 0.0), pointsize=3)
viewer.scene.add(smoothed_points, pointcolor=(1.0, 0.0, 0.0), pointsize=7)
viewer.show()
