import numpy as np
from compas_cgal.reconstruction import pointset_reduction


def test_pointset_reduction():
    # Create a dense point cloud
    x = np.linspace(0, 1, 10)
    y = np.linspace(0, 1, 10)
    X, Y = np.meshgrid(x, y)
    points = np.column_stack((X.ravel(), Y.ravel(), np.zeros_like(X.ravel())))

    # Test point reduction
    spacing = 0.3  # Should reduce points significantly
    reduced_points = pointset_reduction(points, spacing=spacing)

    # Basic checks
    assert reduced_points.shape[0] < points.shape[0]  # Should have fewer points
    assert reduced_points.shape[1] == 3  # Each point should be 3D
