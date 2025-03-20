from pathlib import Path

from compas.geometry import Pointcloud
from compas.geometry import Line
from compas_cgal.reconstruction import pointset_normal_estimation
from compas_cgal.reconstruction import pointset_reduction


def reconstruction_pointset_normal_estimation():
    FILE = Path(__file__).parent.parent / "data" / "box.ply"

    cloud = Pointcloud.from_ply(FILE)
    reduced_cloud = Pointcloud(pointset_reduction(cloud, 1000))
    points, vectors = pointset_normal_estimation(reduced_cloud, 16, True)

    lines = []
    line_scale = 1000

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

    assert len(lines) == len(points)
