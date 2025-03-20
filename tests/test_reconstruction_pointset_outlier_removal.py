from pathlib import Path

from compas.geometry import Pointcloud
from compas_cgal.reconstruction import pointset_outlier_removal
import numpy as np
from line_profiler import profile


@profile
def reconstruction_pointset_outlier_removal():
    FILE = Path(__file__).parent.parent / "data" / "forked_branch_1.ply"
    c1 = Pointcloud.from_ply(FILE)
    points = pointset_outlier_removal(c1, 30, 2.0)
    c2 = Pointcloud(points)
    c3 = c1.difference(c2)
    c2.name = "pointset_outlier_removal"
    c3.name = "pointset_outlier_removal"
    return c2, c3


def test_pointset_outlier_removal():
    # Create a point cloud with an obvious outlier
    points = np.array(
        [
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
            [10, 10, 10],  # Outlier
        ],
        dtype=np.float64,
    )

    # Test outlier removal
    filtered_points = pointset_outlier_removal(points, nnnbrs=3, radius=1.0)

    # Basic checks
    assert filtered_points.shape[0] == 4  # Should have removed one point
    assert filtered_points.shape[1] == 3  # Each point should be 3D
    assert not np.any(np.all(filtered_points == [10, 10, 10], axis=1))  # Outlier should be removed
