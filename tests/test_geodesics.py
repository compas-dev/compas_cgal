from pathlib import Path

import pytest
import numpy as np

from compas.geometry import Sphere
from compas.datastructures import Mesh
from compas_cgal.geodesics import geodesic_isolines
from compas_cgal.geodesics import geodesic_isolines_split
from compas_cgal.geodesics import heat_geodesic_distances
from compas_cgal.geodesics import HeatGeodesicSolver

IFILE = Path(__file__).parent.parent / "data" / "flat_star_disk_irregular_rim.off"


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


def test_heat_geodesic_multisource_boundary_sources():
    """Multi-source accuracy regression: all boundary vertices as the source set.

    The fixture is a FLAT star-shaped disk (z = 0) with irregular, variable-density
    boundary sampling. Because the mesh is flat, the exact geodesic distance to the
    source set in the near-boundary band EQUALS the euclidean distance to the
    nearest source (verified against exact polyhedral geodesics, agreement ~1e-15,
    when the fixture was generated) — the test needs no external oracle, and the
    euclidean distance is a hard LOWER bound everywhere.

    CGAL's ``Heat_method_3`` (backend up to compas_cgal 0.9.4) collapses here: its
    source-set normalization ``min_s |phi(i) - phi(s)|`` folds every vertex whose
    Poisson potential lands inside the source-value spread. Measured on this
    fixture (band = 2h..6h of euclidean distance to the source set):

    - CGAL fold: band mean ratio 0.54, with 83% of band vertices BELOW the
      euclidean lower bound (impossible for a distance).
    - Dirichlet-pinned heat method (this backend): ratio ~0.98, ~1% marginal
      violations, exactly 0 at every source.
    """
    mesh = Mesh.from_off(IFILE)
    V, F = mesh.to_vertices_and_faces()
    V = np.asarray(V, dtype=np.float64)
    F = np.asarray(F, dtype=np.int64)
    sources = sorted({int(v) for v in mesh.vertices_on_boundary()})  # set: compas repeats the loop start
    assert len(sources) == 508  # fixture integrity

    d = heat_geodesic_distances(mesh, sources)  # compas Mesh input (see overload)

    assert np.all(np.isfinite(d))
    assert np.all(d >= 0)
    assert np.allclose(d[sources], 0.0, atol=1e-12)

    # euclidean distance to the nearest source (exact truth in the near band)
    eu = np.sqrt(((V[:, None, :2] - V[sources, :2][None, :, :]) ** 2).sum(-1)).min(axis=1)

    E = np.unique(np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1), axis=0)
    h = float(np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1).mean())
    band = (eu > 2 * h) & (eu < 6 * h)
    assert band.sum() > 1000

    ratio = float(np.mean(d[band] / eu[band]))
    assert 0.85 < ratio < 1.3, f"near-band mean ratio {ratio:.3f} (the CGAL fold reads ~0.54)"

    lb_violations = float(np.mean(d[band] < 0.75 * eu[band]))
    assert lb_violations < 0.10, f"{lb_violations:.0%} of band vertices below the euclidean lower bound (the CGAL fold reads ~83%)"


def test_mesh_input_matches_tuple_input(sphere_mesh):
    """Contract: the compas ``Mesh`` overload agrees with the ``(V, F)`` tuple form.

    Every geodesics entry point accepts either shape; both must coerce through
    ``_as_vertices_faces`` to the same arrays and return identical results.
    """
    V, F = sphere_mesh
    mesh = Mesh.from_vertices_and_faces(V, F)  # key order 0..n-1 preserves source indices
    sources = [0, 10]
    isovalues = [1.0, 2.0]

    assert np.allclose(
        heat_geodesic_distances(mesh, sources),
        heat_geodesic_distances((V, F), sources),
    )

    assert np.allclose(
        HeatGeodesicSolver(mesh).solve(sources),
        HeatGeodesicSolver((V, F)).solve(sources),
    )

    assert len(geodesic_isolines_split(mesh, sources, isovalues)) == len(geodesic_isolines_split((V, F), sources, isovalues))

    assert len(geodesic_isolines(mesh, sources, isovalues)) == len(geodesic_isolines((V, F), sources, isovalues))
