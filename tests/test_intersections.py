import pytest
import numpy as np

from compas.geometry import Box, Frame, Sphere
from compas.geometry import intersection_mesh_mesh


@pytest.fixture
def box_sphere_meshes():
    """Create test meshes: a box and a sphere that intersect."""
    box = Box(2)  # 2x2x2 box centered at origin
    box_mesh = box.to_tessellation().to_vertices_and_triangles()

    sphere = Sphere(1, frame=Frame([1, 1, 1], [1, 0, 0], [0, 1, 0]))
    sphere_mesh = sphere.to_tessellation(nu=32, nv=32).to_vertices_and_triangles()

    return box_mesh, sphere_mesh


def test_intersection_mesh_mesh(box_sphere_meshes):
    """Test mesh-mesh intersection computation."""
    mesh_a, mesh_b = box_sphere_meshes

    # Compute intersections
    pointsets = intersection_mesh_mesh(mesh_a, mesh_b)

    # Basic validation
    assert len(pointsets) > 0, "Should find at least one intersection curve"

    # Validate each pointset
    for points in pointsets:
        assert isinstance(points, np.ndarray), "Each pointset should be a numpy array"
        assert points.shape[1] == 3, "Points should be 3D"
        assert len(points) > 1, "Each intersection curve should have multiple points"


def test_intersection_rejects_invalid_native_result_shape(monkeypatch, box_sphere_meshes):
    mesh_a, mesh_b = box_sphere_meshes
    monkeypatch.setattr(
        "compas_cgal.intersections._intersections.intersection_mesh_mesh",
        lambda *args: [np.empty((0, 2), dtype=np.float64)],
    )

    with pytest.raises(RuntimeError, match="mesh intersection result"):
        intersection_mesh_mesh(mesh_a, mesh_b)
