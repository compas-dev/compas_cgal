import pytest
import numpy as np

from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.isolines import isolines


@pytest.fixture
def sphere_mesh_with_distances():
    """Create a test sphere mesh with geodesic distances as vertex attribute."""
    sphere = Sphere(1.0, point=[0, 0, 0])
    V, F = sphere.to_vertices_and_faces(u=16, v=16, triangulated=True)
    mesh = Mesh.from_vertices_and_faces(V, F)

    # Compute geodesic distances from vertex 0
    distances = heat_geodesic_distances((V, F), [0])

    # Store distances as vertex attribute
    for key, d in zip(mesh.vertices(), distances):
        mesh.vertex_attribute(key, "distance", float(d))

    return mesh


def test_isolines_with_n(sphere_mesh_with_distances):
    """Test isoline extraction with n evenly spaced isovalues."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=5)

    # Should return list of polylines
    assert isinstance(polylines, list)
    assert len(polylines) > 0

    # Each polyline should be a valid Nx3 array
    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.ndim == 2
        assert pts.shape[1] == 3  # 3D points
        assert pts.shape[0] >= 2  # At least 2 points


def test_isolines_with_explicit_isovalues(sphere_mesh_with_distances):
    """Test isoline extraction with explicit isovalue list."""
    mesh = sphere_mesh_with_distances

    # Get distance range to pick valid isovalues
    distances = list(mesh.vertices_attribute("distance"))
    mid_val = (min(distances) + max(distances)) / 2

    polylines = isolines(mesh, "distance", isovalues=[mid_val])

    assert isinstance(polylines, list)
    assert len(polylines) > 0

    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3


def test_isolines_validation_neither_provided(sphere_mesh_with_distances):
    """Test that ValueError is raised when neither isovalues nor n is provided."""
    mesh = sphere_mesh_with_distances

    with pytest.raises(ValueError, match="Either 'isovalues' or 'n' must be provided"):
        isolines(mesh, "distance")


def test_isolines_validation_both_provided(sphere_mesh_with_distances):
    """Test that ValueError is raised when both isovalues and n are provided."""
    mesh = sphere_mesh_with_distances

    with pytest.raises(ValueError, match="Provide exactly one of 'isovalues' or 'n'"):
        isolines(mesh, "distance", isovalues=[1.0], n=5)


def test_isolines_empty_result(sphere_mesh_with_distances):
    """Test isolines with isovalue outside scalar range returns empty list."""
    mesh = sphere_mesh_with_distances

    # Use isovalue way outside the distance range
    polylines = isolines(mesh, "distance", isovalues=[1000.0])

    assert isinstance(polylines, list)
    assert len(polylines) == 0


def test_isolines_with_smoothing(sphere_mesh_with_distances):
    """Test isoline extraction with smoothing enabled."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=3, smoothing=2)

    assert isinstance(polylines, list)
    assert len(polylines) > 0

    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3


def test_isolines_with_resample_int(sphere_mesh_with_distances):
    """Test isoline extraction with integer resampling factor."""
    mesh = sphere_mesh_with_distances

    polylines_no_resample = isolines(mesh, "distance", n=3, resample=False)
    polylines_resample = isolines(mesh, "distance", n=3, resample=4)

    # Resampled polylines should generally have more points
    if len(polylines_no_resample) > 0 and len(polylines_resample) > 0:
        total_pts_no_resample = sum(len(pl) for pl in polylines_no_resample)
        total_pts_resample = sum(len(pl) for pl in polylines_resample)
        assert total_pts_resample >= total_pts_no_resample


def test_isolines_resample_disabled(sphere_mesh_with_distances):
    """Test isoline extraction with resampling disabled."""
    mesh = sphere_mesh_with_distances

    polylines = isolines(mesh, "distance", n=3, resample=False)

    assert isinstance(polylines, list)
    # Result should still be valid polylines
    for pts in polylines:
        assert isinstance(pts, np.ndarray)
        assert pts.shape[1] == 3
