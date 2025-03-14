from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_cgal.reconstruction import pointset_smoothing
from compas.geometry import transform_points_numpy
from compas_viewer import Viewer
from compas_viewer.config import Config
from line_profiler import profile


@profile
def reconstruction_pointset_smoothing():
    """Smooth a point set."""

    ply_file_path = Path(__file__).parent.parent.parent / "data" / "box.ply"
    original_points = Pointcloud.from_ply(ply_file_path)

    smoothed_points = pointset_smoothing(original_points, 1000, 3)

    return Pointcloud(original_points), Pointcloud(smoothed_points)


c_smoothing_0, c_smoothing_1 = reconstruction_pointset_smoothing()

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.camera.target = [0, 5000, -10000]
config.camera.position = [0, -10000, 30000]
config.camera.scale = 1000
config.renderer.gridsize = (20000, 20, 20000, 20)

viewer = Viewer(config=config)
viewer.scene.add(c_smoothing_0, pointcolor=(0.0, 0.0, 0.0))
viewer.scene.add(c_smoothing_1, pointcolor=(1.0, 0.0, 0.0))
viewer.show()
