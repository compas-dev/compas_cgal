from pathlib import Path

from compas.geometry import Pointcloud
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.reconstruction import pointset_outlier_removal

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

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.unit = "mm"

viewer = Viewer(config=config)

viewer.scene.add(c2, pointcolor=(0.0, 0.0, 0.0))
viewer.scene.add(c3, pointcolor=(1.0, 0.0, 0.0))

viewer.show()
