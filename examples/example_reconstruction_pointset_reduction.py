from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.config import Config

from compas_cgal.reconstruction import pointset_reduction

# =============================================================================
# Input
# =============================================================================

FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"
cloud = Pointcloud.from_ply(FILE)

# =============================================================================
# Reduction
# =============================================================================

cloud_reduced = Pointcloud(pointset_reduction(cloud, 50))
cloud_reduced.transform(Translation.from_vector([-1000, 0, 0]))

# =============================================================================
# Viz
# =============================================================================

config = Config()
config.unit = "mm"

viewer = Viewer(config=config)

viewer.scene.add(cloud, pointcolor=(0.0, 0.0, 0.0))
viewer.scene.add(cloud_reduced, pointcolor=(1.0, 0.0, 0.0))

viewer.show()
