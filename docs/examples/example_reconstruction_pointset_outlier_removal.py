from pathlib import Path

from compas.geometry import Pointcloud
from compas_cgal.reconstruction import pointset_outlier_removal
from compas_viewer import Viewer
from compas_viewer.config import Config
from line_profiler import profile


@profile
def reconstruction_pointset_outlier_removal():
    """Remove outliers from a point set."""

    # ==============================================================================
    # Input geometry
    # ==============================================================================

    FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"
    c1 = Pointcloud.from_ply(FILE)

    # ==============================================================================
    # Compute
    # ==============================================================================

    points = pointset_outlier_removal(c1, 30, 2.0)
    c2 = Pointcloud(points)
    c3 = c1.difference(c2)

    return c2, c3


c_outlier_removal_0, c_outlier_removal_1 = reconstruction_pointset_outlier_removal()

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.camera.target = [600, 500, 200]
config.camera.position = [600, -1000, 1500]
config.camera.scale = 100
config.renderer.gridsize = (20000, 20, 20000, 20)

viewer = Viewer(config=config)

viewer.scene.add(c_outlier_removal_0, pointcolor=(0.0, 0.0, 0.0))
viewer.scene.add(c_outlier_removal_1, pointcolor=(1.0, 0.0, 0.0))

viewer.show()
