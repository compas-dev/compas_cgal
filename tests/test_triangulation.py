import numpy as np
import pytest

import compas_cgal.plugins.triangulation as plugin_triangulation
import compas_cgal.triangulation as cgal_triangulation
from compas.geometry import Frame
from compas.geometry import Polygon
from compas.geometry import PolygonalSurface
from compas.geometry import Translation
from compas.geometry import conforming_delaunay_triangulation
from compas.geometry import constrained_delaunay_triangulation
from compas.geometry import delaunay_triangulation


@pytest.fixture
def boundary_polygon():
    return Polygon.from_sides_and_radius_xy(32, 4)


@pytest.fixture
def hole_polygons():
    hole = Polygon.from_sides_and_radius_xy(32, 0.5)
    return [
        hole.transformed(Translation.from_vector([2, 0, 0])),
        hole.transformed(Translation.from_vector([-2, 0, 0])),
    ]


def test_strategy_era_triangulation_paths_are_removed():
    for module in (cgal_triangulation, plugin_triangulation):
        assert not hasattr(module, "_triangulate_planar_points")
        assert not hasattr(module, "_triangulate_planar_domain")


def test_delaunay_returns_structural_buffers_and_preserves_points(boundary_polygon):
    points = [list(point) for point in boundary_polygon.points]
    vertices, triangles = delaunay_triangulation(points)

    assert vertices == points
    assert triangles
    assert all(len(triangle) == 3 for triangle in triangles)


@pytest.mark.parametrize(
    "points",
    [
        np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float32),
        np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float64),
        np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.int32),
        np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.int64),
        np.asfortranarray(np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float64)),
        np.asarray([[0, 0, 0, 9], [2, 0, 0, 9], [0, 2, 0, 9]], dtype=np.float64)[:, :3],
    ],
)
def test_delaunay_accepts_numpy_coordinate_buffers_without_mutation(points):
    points_before = points.copy()

    vertices, triangles = delaunay_triangulation(points)

    assert len(vertices) == len(points)
    assert triangles
    np.testing.assert_array_equal(points, points_before)


def test_delaunay_accepts_readonly_numpy_coordinates():
    points = np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float64)
    points.flags.writeable = False

    vertices, triangles = delaunay_triangulation(points)

    assert len(vertices) == len(points)
    assert triangles


def test_direct_delaunay_returns_exact_result_contract_and_coalesces_duplicates():
    points = [[0, 0, 0], [2, 0, 0], [0, 2, 0], [0, 0, 0]]

    vertices, triangles = cgal_triangulation.delaunay_triangulation(points)

    assert vertices == points[:3]
    assert triangles.dtype == np.int32
    assert triangles.flags.c_contiguous
    assert triangles.shape == (1, 3)
    a, b, c = np.asarray(vertices)[triangles[0]]
    assert np.cross(b - a, c - a)[2] > 0
    surface = PolygonalSurface(vertices, triangles)
    assert len(surface.faces) == 1


def test_direct_delaunay_reorients_native_clockwise_triangles(monkeypatch):
    monkeypatch.setattr(
        cgal_triangulation._triangulation,
        "delaunay_triangulation",
        lambda points: np.asarray([[0, 2, 1]], dtype=np.int64),
    )

    vertices, triangles = cgal_triangulation.delaunay_triangulation([[0, 0, 0], [2, 0, 0], [0, 2, 0]])

    assert vertices == [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]]
    np.testing.assert_array_equal(triangles, [[0, 1, 2]])


def test_direct_delaunay_rejects_malformed_native_results(monkeypatch):
    monkeypatch.setattr(
        cgal_triangulation._triangulation,
        "delaunay_triangulation",
        lambda points: np.asarray([[0, 1, 3]], dtype=np.int32),
    )

    with pytest.raises(RuntimeError, match="in range"):
        cgal_triangulation.delaunay_triangulation([[0, 0, 0], [2, 0, 0], [0, 2, 0]])


def test_constrained_domain_returns_structural_buffers(boundary_polygon, hole_polygons):
    vertices, triangles = constrained_delaunay_triangulation(
        boundary_polygon,
        holes=hole_polygons,
    )

    assert vertices
    assert triangles
    assert all(len(triangle) == 3 for triangle in triangles)


def test_constrained_domain_accepts_numpy_coordinate_collections_without_mutation():
    boundary = np.asfortranarray(np.asarray([[0, 0, 0], [4, 0, 0], [4, 4, 0], [0, 4, 0]], dtype=np.float32))
    holes = np.asarray(
        [[[1, 1, 0], [1, 2, 0], [2, 2, 0], [2, 1, 0]]],
        dtype=np.float64,
    )
    constraints = np.asarray([[[0, 3, 0], [4, 3, 0]]], dtype=np.float32)
    points = np.asarray([[3, 1, 0]], dtype=np.float64)
    holes.flags.writeable = False
    before = [array.copy() for array in (boundary, holes, constraints, points)]

    vertices, triangles = constrained_delaunay_triangulation(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
    )

    assert vertices
    assert triangles
    for array, expected in zip((boundary, holes, constraints, points), before, strict=True):
        np.testing.assert_array_equal(array, expected)


def test_conforming_domain_supports_maximum_edge_length(boundary_polygon, hole_polygons):
    maximum = 0.5
    vertices, triangles = conforming_delaunay_triangulation(
        boundary_polygon,
        holes=hole_polygons,
        max_edge_length=maximum,
    )

    edges = {tuple(sorted((int(face[index]), int(face[(index + 1) % 3])))) for face in triangles for index in range(3)}
    for u, v in edges:
        length = np.linalg.norm(np.asarray(vertices[u]) - np.asarray(vertices[v]))
        assert length <= maximum * 1.1


def test_conforming_domain_accepts_omitted_aggregate_defaults(boundary_polygon):
    vertices, triangles = conforming_delaunay_triangulation(boundary_polygon, max_edge_length=None)

    assert vertices
    assert triangles


@pytest.mark.parametrize("value", [0.0, -1.0, float("inf")])
def test_conforming_domain_requires_positive_finite_max_edge_length(boundary_polygon, value):
    with pytest.raises(ValueError, match="positive and finite"):
        conforming_delaunay_triangulation(boundary_polygon, max_edge_length=value)


@pytest.mark.parametrize("value", [True, "1"])
def test_cgal_conforming_rejects_non_real_max_edge_length(boundary_polygon, value):
    with pytest.raises(TypeError, match="real number"):
        cgal_triangulation.conforming_delaunay_triangulation(boundary_polygon, max_edge_length=value)


def test_explicit_frame_preserves_input_coordinates():
    frame = Frame([0, 0, 2], [1, 0, 0], [0, 1, 0])
    boundary = [[0, 0, 2], [2, 0, 2], [2, 2, 2], [0, 2, 2]]
    vertices, _ = constrained_delaunay_triangulation(boundary, frame=frame)

    output = {tuple(point) for point in vertices}
    assert all(tuple(point) in output for point in boundary)


def test_conforming_lifts_steiner_vertices_to_explicit_frame():
    frame = Frame.worldYZ()
    boundary = [[0, 0, 0], [0, 2, 0], [0, 2, 2], [0, 0, 2]]
    vertices, _ = conforming_delaunay_triangulation(boundary, max_edge_length=0.5, frame=frame)

    output = {tuple(point) for point in vertices}
    assert all(tuple(point) in output for point in boundary)
    assert all(point[0] == pytest.approx(0.0) for point in vertices)


def test_planarity_is_validated():
    boundary = [[0, 0, 0], [2, 0, 0], [2, 2, 0.1], [0, 2, 0]]
    with pytest.raises(ValueError, match="world XY"):
        constrained_delaunay_triangulation(boundary)


def test_native_boundary_sizes_are_validated():
    with pytest.raises(ValueError, match="Delaunay input"):
        delaunay_triangulation([[0, 0, 0], [1, 0, 0]])
    with pytest.raises(ValueError, match="Boundary"):
        constrained_delaunay_triangulation([[0, 0, 0], [1, 0, 0]])
    with pytest.raises(ValueError, match="Hole"):
        constrained_delaunay_triangulation(
            [[0, 0, 0], [2, 0, 0], [0, 2, 0]],
            holes=[[[0.5, 0.5, 0], [1.0, 0.5, 0]]],
        )
