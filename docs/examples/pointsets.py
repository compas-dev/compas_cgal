from pathlib import Path

from compas.geometry import Pointcloud
from compas_cgal.reconstruction import pointset_outlier_removal
from compas_viewer import Viewer

FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"

cloud1 = Pointcloud.from_ply(FILE)

points = pointset_outlier_removal(cloud1, 30, 2.0)

cloud2 = Pointcloud(points)
could3 = cloud1.difference(cloud2)

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()

# viewer.view.camera.scale = 1000
# viewer.view.grid.cell_size = 1000

viewer.scene.add(cloud2)
viewer.scene.add(could3, pointcolor=(1.0, 0.0, 0.0))

# viewer.view.camera.zoom_extents()
viewer.show()
