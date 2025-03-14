from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas.geometry import transform_points_numpy
from compas_cgal.reconstruction import pointset_reduction
from compas_viewer import Viewer
from compas_viewer.config import Config
from line_profiler import profile


@profile
def reconstruction_pointset_reduction():
    """Reduce the number of points in a point set."""

    FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"
    c = Pointcloud.from_ply(FILE)

    points = Pointcloud(pointset_reduction(c, 50))
    transform_points_numpy(points, Translation.from_vector([-1000, 0, 0]))

    c.transform(Translation.from_vector([-1000, 0, 0]))

    return c, points


c_reduction_0, c_reduction_1 = reconstruction_pointset_reduction()

config = Config()
config.camera.target = [100, 500, 200]
config.camera.position = [100, -1500, 2000]
config.camera.scale = 100
config.renderer.gridsize = (20000, 20, 20000, 20)

viewer = Viewer(config=config)
viewer.scene.add(c_reduction_0, pointcolor=(0.0, 0.0, 0.0))
viewer.scene.add(c_reduction_1, pointcolor=(1.0, 0.0, 0.0))

viewer.show()
