import numpy as np
from compas_cgal.reconstruction import pointset_smoothing


def test_pointset_smoothing():
    # Create a noisy point cloud
    points = np.array(
        [
            [0, 0, 0],
            [1.1, 0.1, 0.1],  # Noisy point
            [0, 1, 0],
            [0.9, 0.9, -0.1],  # Noisy point
        ],
        dtype=np.float64,
    )

    # Test smoothing
    smoothed_points = pointset_smoothing(points, neighbors=3, iterations=2)

    # Basic checks
    assert smoothed_points.shape == points.shape  # Should preserve point count
    assert smoothed_points.shape[1] == 3  # Each point should be 3D
