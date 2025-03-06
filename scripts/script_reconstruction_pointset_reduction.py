from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_cgal.reconstruction import pointset_reduction
from compas_viewer import Viewer
from line_profiler import profile


@profile
def reconstruction_pointset_reduction():
    FILE = Path(__file__).parent.parent / "data" / "forked_branch_1.ply"
    c = Pointcloud.from_ply(FILE)
    c.transform(Translation.from_vector([-1000, 0, 0]))
    points = Pointcloud(pointset_reduction(c, 50))
    return c, points


if __name__ == "__main__":
    c_reduction_0, c_reduction_1 = reconstruction_pointset_reduction()
    viewer = Viewer(width=1600, height=900)
    viewer.scene.add(c_reduction_0, pointcolor=(0.0, 1.0, 0.0))
    viewer.scene.add(c_reduction_1, pointcolor=(0.0, 0.0, 1.0))
    viewer.show()
