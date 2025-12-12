"""Tests for COMPAS CGAL geodesics functionality."""

import pytest
import numpy as np

from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas_cgal.geodesics import geodesic_isolines
from compas_cgal.geodesics import geodesic_isolines_split
from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.geodesics import HeatGeodesicSolver


@pytest.fixture
def sphere_mesh():
    """Create a test sphere mesh."""
    sphere = Sphere(1.0, point=[0, 0, 0])
    V, F = sphere.to_vertices_and_faces(u=16, v=16, triangulated=True)
    return V, F


def test_heat_geodesic_distances_basic(sphere_mesh):
    """Test basic geodesic distance computation."""
    V, F = sphere_mesh
    sources = [0]

    distances = heat_geodesic_distances((V, F), sources)

    # Basic validation
    assert isinstance(distances, np.ndarray)
    assert distances.shape[0] == len(V)  # One distance per vertex
    assert distances.ndim == 1  # Should be 1D array
    assert distances[0] == pytest.approx(0.0)  # Distance from source to itself is 0
    assert np.all(distances >= 0)  # All distances should be non-negative
    assert np.all(np.isfinite(distances))  # No inf or nan values


def test_heat_geodesic_distances_multiple_sources(sphere_mesh):
    """Test geodesic distance computation with multiple sources."""
    V, F = sphere_mesh
    sources = [0, 10, 20]

    distances = heat_geodesic_distances((V, F), sources)

    # Validate shape and properties
    assert isinstance(distances, np.ndarray)
    assert distances.shape[0] == len(V)
    assert np.all(distances >= 0)

    # All source vertices should have distance 0
    for source_idx in sources:
        assert distances[source_idx] == pytest.approx(0.0, abs=1e-6)


def test_heat_geodesic_solver_basic(sphere_mesh):
    """Test HeatGeodesicSolver for single query."""
    V, F = sphere_mesh

    solver = HeatGeodesicSolver((V, F))

    # Check num_vertices property
    assert solver.num_vertices == len(V)

    # Solve from single source
    distances = solver.solve([0])

    assert isinstance(distances, np.ndarray)
    assert distances.shape[0] == len(V)
    assert distances[0] == pytest.approx(0.0)
    assert np.all(distances >= 0)


def test_heat_geodesic_solver_multiple_queries(sphere_mesh):
    """Test HeatGeodesicSolver for multiple queries (efficiency use case)."""
    V, F = sphere_mesh

    solver = HeatGeodesicSolver((V, F))

    # Solve multiple times from different sources
    d0 = solver.solve([0])
    d1 = solver.solve([5])
    d2 = solver.solve([10])

    # Each should be valid
    for distances in [d0, d1, d2]:
        assert isinstance(distances, np.ndarray)
        assert distances.shape[0] == len(V)
        assert np.all(distances >= 0)

    # Different sources should yield different distance fields
    assert not np.allclose(d0, d1)
    assert not np.allclose(d1, d2)


def test_geodesic_distances_consistency(sphere_mesh):
    """Test that function and solver produce same results."""
    V, F = sphere_mesh
    sources = [0]

    # Compute with function
    d_func = heat_geodesic_distances((V, F), sources)

    # Compute with solver
    solver = HeatGeodesicSolver((V, F))
    d_solver = solver.solve(sources)

    # Should be approximately equal
    assert np.allclose(d_func, d_solver, rtol=1e-5)


def test_geodesic_distances_mesh_conversion(sphere_mesh):
    """Test compatibility with COMPAS Mesh objects."""
    V, F = sphere_mesh

    # Create a Mesh object and convert back
    mesh = Mesh.from_vertices_and_faces(V, F)
    V2, F2 = mesh.to_vertices_and_faces()

    # Compute distances
    distances = heat_geodesic_distances((V2, F2), [0])

    assert isinstance(distances, np.ndarray)
    assert distances.shape[0] == len(V2)
    assert distances[0] == pytest.approx(0.0)


def test_geodesic_isolines_split(sphere_mesh):
    """Test splitting mesh along geodesic isolines."""
    V, F = sphere_mesh

    components = geodesic_isolines_split((V, F), [0], [1.0, 2.0])

    # Should return list of (vertices, faces) tuples
    assert isinstance(components, list)
    assert len(components) > 1  # Should have multiple components

    # Each component should be valid mesh data
    total_faces = 0
    for v, f in components:
        assert isinstance(v, np.ndarray)
        assert isinstance(f, np.ndarray)
        assert v.shape[1] == 3  # 3D vertices
        assert f.shape[1] == 3  # Triangle faces
        assert f.min() >= 0
        assert f.max() < len(v)
        total_faces += len(f)

    # Total faces should be >= original (refinement adds faces)
    assert total_faces >= len(F)


def test_geodesic_isolines(sphere_mesh):
    """Test extracting isoline polylines."""
    V, F = sphere_mesh

    isolines = geodesic_isolines((V, F), [0], [1.0, 2.0])

    # Should return list of connected polylines
    assert isinstance(isolines, list)
    assert len(isolines) > 0  # Should have some isolines

    # Each polyline should have multiple points
    for pts in isolines:
        assert isinstance(pts, np.ndarray)
        assert pts.ndim == 2
        assert pts.shape[1] == 3  # 3D points
        assert pts.shape[0] >= 2  # At least 2 points


def test_geodesic_isolines_empty(sphere_mesh):
    """Test isolines with no crossings."""
    V, F = sphere_mesh

    # Use isovalue outside the distance range
    isolines = geodesic_isolines((V, F), [0], [100.0])

    # Should return empty list
    assert isinstance(isolines, list)
    assert len(isolines) == 0
