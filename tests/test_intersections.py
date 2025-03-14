import pytest
import numpy as np

from compas.geometry import Box, Sphere
from compas_cgal.intersections import intersection_mesh_mesh

from compas_cgal.compas_cgal_ext import VectorRowMatrixXd


@pytest.fixture
def box_sphere_meshes():
    """Create test meshes: a box and a sphere that intersect."""
    box = Box(2)  # 2x2x2 box centered at origin
    box_mesh = box.to_vertices_and_faces(triangulated=True)

    sphere = Sphere(1, point=[1, 1, 1])  # Sphere radius 1, centered at [1,1,1]
    sphere_mesh = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

    return box_mesh, sphere_mesh


def test_intersection_mesh_mesh(box_sphere_meshes):
    """Test mesh-mesh intersection computation."""
    mesh_a, mesh_b = box_sphere_meshes

    # Compute intersections
    pointsets = intersection_mesh_mesh(mesh_a, mesh_b)

    # Basic validation
    assert isinstance(pointsets, VectorRowMatrixXd), "Result should be a nanobind type"
    assert len(pointsets) > 0, "Should find at least one intersection curve"

    # Validate each pointset
    for points in pointsets:
        assert isinstance(points, np.ndarray), "Each pointset should be a numpy array"
        assert points.shape[1] == 3, "Points should be 3D"
        assert len(points) > 1, "Each intersection curve should have multiple points"
