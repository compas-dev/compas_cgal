from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Line
from compas_cgal.reconstruction import pointset_normal_estimation
from compas_cgal.reconstruction import pointset_reduction
from compas_viewer import Viewer
from compas_viewer.scene import Collection
from compas_viewer.config import Config
from line_profiler import profile


@profile
def reconstruction_pointset_normal_estimation():
    # ==============================================================================
    # Input geometry
    # ==============================================================================

    FILE = Path(__file__).parent.parent.parent / "data" / "forked_branch_1.ply"

    cloud = Pointcloud.from_ply(FILE)
    reduced_cloud = Pointcloud(pointset_reduction(cloud, 10))
    points, vectors = pointset_normal_estimation(reduced_cloud, 16, True)

    # ==============================================================================
    # Compute
    # ==============================================================================

    lines = []
    line_scale = 10

    for p, v in zip(points, vectors):
        line = Line(
            [p[0], p[1], p[2]],
            [
                p[0] + v[0] * line_scale,
                p[1] + v[1] * line_scale,
                p[2] + v[2] * line_scale,
            ],
        )
        lines.append(line)

    return lines


lines = reconstruction_pointset_normal_estimation()

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.camera.target = [600, 500, 200]
config.camera.position = [600, -1000, 1500]
config.camera.scale = 100
config.renderer.gridsize = (20000, 20, 20000, 20)

viewer = Viewer(config=config)
viewer.scene.add(Collection(lines))
viewer.show()
