"""Contract tests for the exact polyhedral geodesic backend.

Analytic accuracy lives in `test_geodesics_exact_analytic.py`. This file pins the
contracts BETWEEN the entry points -- that a point source coinciding with a vertex
agrees with the vertex-source path, that nearest-source ordinals index the caller's
own sequence, and that every failure mode raises rather than returning a wrong field.
"""

import numpy as np
import pytest

from compas_cgal.geodesics import ExactGeodesicSolver
from compas_cgal.geodesics import exact_geodesic_distances
from compas_cgal.geodesics import exact_geodesic_distances_from_points

# A source vertex's own distance is zero by construction, so anything above pure
# accumulation round-off on a unit-scale fixture is a defect, not noise.
SOURCE_SELF_DISTANCE_ATOL = 1e-12

# The planar plate's analytic field is exact for the polyhedron (see the analytic
# suite), so the only residual is float64 arithmetic: ~4 ulp of the unit fixture.
PLANAR_ANALYTIC_ATOL = 1e-12

# Grid sizes exercising the barycentric-snap regression. On CGAL 6.1.1 without the
# snap in geodesics_exact.cpp, n = 4, 6 and 7 each mis-root exactly one corner while
# 5, 8 and 9 happen to survive -- the classification turns on the last bit, so the
# regression must sweep sizes rather than pick one.
SNAP_REGRESSION_GRID_SIZES = (4, 5, 6, 7, 8, 9)


def unit_plate(n):
    """Triangulated unit square as (vertices, faces), n x n vertices."""
    xs = np.linspace(0.0, 1.0, n)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    vertices = np.column_stack([X.ravel(), Y.ravel(), np.zeros(n * n)])
    faces = []
    for i in range(n - 1):
        for j in range(n - 1):
            a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j, (i + 1) * n + j + 1
            faces += [[a, b, d], [a, d, c]]
    return np.ascontiguousarray(vertices), np.ascontiguousarray(faces, dtype=np.int32)


def plate_boundary(n):
    """Indices of the plate's boundary vertices."""
    return [i * n + j for i in range(n) for j in range(n) if i in (0, n - 1) or j in (0, n - 1)]


@pytest.mark.parametrize("n", SNAP_REGRESSION_GRID_SIZES)
def test_every_vertex_is_its_own_nearest_source_as_a_point(n):
    """A point source AT a vertex must give that vertex distance zero.

    Regression for the barycentric-snap defect: CGAL's `locate()` returns coordinates
    carrying construction round-off for a point lying exactly on a vertex, while
    `Classify_barycentric_coordinates` tests exactly. Unsnapped, the wavefront roots at
    the wrong vertex and this reads one edge length instead of zero -- silently.
    """
    vertices, faces = unit_plate(n)
    offenders = [k for k in range(len(vertices)) if exact_geodesic_distances_from_points((vertices, faces), vertices[[k]])[k] > SOURCE_SELF_DISTANCE_ATOL]
    assert offenders == [], f"n={n}: vertices mis-rooted as their own point source: {offenders}"


def test_point_sources_at_vertices_reproduce_the_vertex_source_field():
    """The contract linking the two entry points: same sources, same field."""
    n = 21
    vertices, faces = unit_plate(n)
    boundary = plate_boundary(n)
    from_vertices = exact_geodesic_distances((vertices, faces), boundary)
    from_points = exact_geodesic_distances_from_points((vertices, faces), vertices[boundary])
    assert np.array_equal(from_vertices, from_points), f"max |difference| {np.abs(from_vertices - from_points).max():.3e}"


def test_planar_plate_matches_the_euclidean_analytic_field():
    """On a planar domain the geodesic distance from the boundary is euclidean."""
    n = 21
    vertices, faces = unit_plate(n)
    boundary = plate_boundary(n)
    analytic = np.minimum.reduce([vertices[:, 0], 1.0 - vertices[:, 0], vertices[:, 1], 1.0 - vertices[:, 1]])
    measured = exact_geodesic_distances((vertices, faces), boundary)
    assert np.abs(measured - analytic).max() < PLANAR_ANALYTIC_ATOL


def test_nearest_source_ordinal_indexes_the_callers_own_sequence():
    """`sources[ordinal]` must recover the source vertex, for any source ordering."""
    n = 11
    vertices, faces = unit_plate(n)
    boundary = plate_boundary(n)[::-1]
    distances, ordinals = exact_geodesic_distances((vertices, faces), boundary, return_sources=True)
    assert ordinals.min() >= 0 and ordinals.max() < len(boundary)
    recovered = np.asarray(boundary)[ordinals]
    assert np.abs(distances[recovered]).max() < SOURCE_SELF_DISTANCE_ATOL
    assert np.abs(distances[boundary]).max() < SOURCE_SELF_DISTANCE_ATOL


def test_solver_agrees_with_the_free_functions_and_reuses_the_mesh():
    n = 11
    vertices, faces = unit_plate(n)
    boundary = plate_boundary(n)
    solver = ExactGeodesicSolver((vertices, faces))
    assert solver.num_vertices == len(vertices)
    assert np.array_equal(solver.solve(boundary), exact_geodesic_distances((vertices, faces), boundary))
    # a second source set on the same solver must not be contaminated by the first
    assert np.array_equal(solver.solve([0]), exact_geodesic_distances((vertices, faces), [0]))
    assert np.array_equal(
        solver.solve_from_points(vertices[boundary]),
        exact_geodesic_distances_from_points((vertices, faces), vertices[boundary]),
    )


def test_out_of_range_sources_are_ignored_and_duplicates_collapse():
    n = 11
    vertices, faces = unit_plate(n)
    plain = exact_geodesic_distances((vertices, faces), [0, 5])
    noisy = exact_geodesic_distances((vertices, faces), [0, 5, 5, -1, 10**6, 0])
    assert np.array_equal(plain, noisy)


def test_empty_source_set_raises():
    vertices, faces = unit_plate(5)
    with pytest.raises(ValueError):
        exact_geodesic_distances((vertices, faces), [])
    with pytest.raises(ValueError):
        exact_geodesic_distances((vertices, faces), [-1, 10**6])


def test_malformed_source_points_raise():
    vertices, faces = unit_plate(5)
    with pytest.raises(ValueError):
        exact_geodesic_distances_from_points((vertices, faces), np.zeros((0, 3)))
    with pytest.raises(ValueError):
        exact_geodesic_distances_from_points((vertices, faces), np.zeros((2, 2)))
    with pytest.raises(ValueError):
        exact_geodesic_distances_from_points((vertices, faces), np.array([[0.0, 0.0, np.nan]]))


def test_a_component_without_a_source_raises_rather_than_returning_a_wrong_field():
    """Two disjoint plates, sources on one only: the other has no defined distance."""
    left_v, left_f = unit_plate(5)
    right_v, right_f = unit_plate(5)
    right_v = right_v + np.array([10.0, 0.0, 0.0])
    vertices = np.ascontiguousarray(np.vstack([left_v, right_v]))
    faces = np.ascontiguousarray(np.vstack([left_f, right_f + len(left_v)]), dtype=np.int32)
    with pytest.raises(RuntimeError):
        exact_geodesic_distances((vertices, faces), [0])


def test_nearest_source_ordinal_survives_filtering_of_the_source_list():
    """Ordinals index the sequence AS GIVEN, never the accepted subset.

    The backend drops out-of-range indices and collapses duplicates. Were the ordinal a
    running count of accepted sources, ``sources[ordinal]`` would name the wrong vertex
    for every region nearest a source that follows a dropped entry -- silently, and only
    for part of the mesh. Reversing a clean source list does not exercise this; the list
    has to actually lose entries.
    """
    n = 11
    vertices, faces = unit_plate(n)
    corner, far = 0, n * n - 1
    sources = [10**6, corner, corner, -1, far]  # two dropped, one duplicate
    distances, ordinals = exact_geodesic_distances((vertices, faces), sources, return_sources=True)

    # position in the GIVEN list, not rank among survivors (which would be 0 and 1)
    assert ordinals[corner] == 1, "duplicate sources must resolve to the first occurrence"
    assert ordinals[far] == 4, "ordinal must index the sequence as given"

    recovered = np.asarray(sources)[ordinals]
    assert set(np.unique(recovered).tolist()) <= {corner, far}
    assert np.abs(distances[recovered]).max() < SOURCE_SELF_DISTANCE_ATOL


def test_duplicate_point_sources_are_kept_rather_than_collapsed():
    """Point sources do NOT collapse, unlike vertex sources -- pinned as documented.

    Collapsing them would require an equality test on coordinates, i.e. a positional
    tolerance, which this module deliberately does not own. The consequence is that a
    repeated sample yields a repeated ordinal, and the field is unaffected.
    """
    n = 11
    vertices, faces = unit_plate(n)
    once = exact_geodesic_distances_from_points((vertices, faces), vertices[[0]])
    twice, ordinals = exact_geodesic_distances_from_points((vertices, faces), vertices[[0, 0]], return_sources=True)
    assert np.array_equal(once, twice), "a repeated source point must not change the field"
    assert set(np.unique(ordinals).tolist()) <= {0, 1}
