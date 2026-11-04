import numpy as np
import pytest

from compas.geometry import ConformingDelaunay
from compas.geometry import ConstrainedDelaunay
from compas.geometry import Delaunay
from compas.geometry import Frame
from compas.geometry import Polygon
from compas.geometry import Tessellation
from compas.geometry import Translation
from compas.geometry import TriangulationQuality
from compas.geometry import triangulate_planar_domain
from compas.geometry import triangulate_planar_points


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


def test_delaunay_returns_tessellation_and_preserves_points(boundary_polygon):
    points = [list(point) for point in boundary_polygon.points]
    result = triangulate_planar_points(points, strategy=Delaunay())

    assert isinstance(result, Tessellation)
    assert result.vertices == points
    assert isinstance(result.triangles, np.ndarray)
    assert result.triangles.dtype == np.int32
    assert result.triangles.flags.c_contiguous


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

    result = triangulate_planar_points(points, strategy=Delaunay())

    assert isinstance(result, Tessellation)
    np.testing.assert_array_equal(points, points_before)


def test_delaunay_accepts_readonly_numpy_coordinates():
    points = np.asarray([[0, 0, 0], [2, 0, 0], [0, 2, 0]], dtype=np.float64)
    points.flags.writeable = False

    result = triangulate_planar_points(points, strategy=Delaunay())

    assert isinstance(result, Tessellation)


def test_constrained_domain_returns_tessellation(boundary_polygon, hole_polygons):
    result = triangulate_planar_domain(
        boundary_polygon,
        holes=hole_polygons,
        strategy=ConstrainedDelaunay(),
    )

    assert isinstance(result, Tessellation)
    assert result.number_of_vertices > 0
    assert result.number_of_triangles > 0
    assert isinstance(result.triangles, np.ndarray)
    assert result.triangles.dtype == np.int32


def test_constrained_domain_accepts_numpy_coordinate_collections_without_mutation():
    boundary = np.asfortranarray(
        np.asarray([[0, 0, 0], [4, 0, 0], [4, 4, 0], [0, 4, 0]], dtype=np.float32)
    )
    holes = np.asarray(
        [[[1, 1, 0], [1, 2, 0], [2, 2, 0], [2, 1, 0]]],
        dtype=np.float64,
    )
    constraints = np.asarray([[[0, 3, 0], [4, 3, 0]]], dtype=np.float32)
    points = np.asarray([[3, 1, 0]], dtype=np.float64)
    holes.flags.writeable = False
    before = [array.copy() for array in (boundary, holes, constraints, points)]

    result = triangulate_planar_domain(
        boundary,
        holes=holes,
        constraints=constraints,
        points=points,
        strategy=ConstrainedDelaunay(),
    )

    assert isinstance(result, Tessellation)
    for array, expected in zip((boundary, holes, constraints, points), before, strict=True):
        np.testing.assert_array_equal(array, expected)


def test_conforming_domain_supports_maximum_edge_length(boundary_polygon, hole_polygons):
    maximum = 0.5
    result = triangulate_planar_domain(
        boundary_polygon,
        holes=hole_polygons,
        strategy=ConformingDelaunay(TriangulationQuality(max_edge_length=maximum)),
    )

    edges = {tuple(sorted((int(face[index]), int(face[(index + 1) % 3])))) for face in result.triangles for index in range(3)}
    for u, v in edges:
        length = np.linalg.norm(np.asarray(result.vertices[u]) - np.asarray(result.vertices[v]))
        assert length <= maximum * 1.1


@pytest.mark.parametrize(
    "quality",
    [TriangulationQuality(min_angle=20.0), TriangulationQuality(max_area=0.5)],
)
def test_conforming_domain_rejects_unsupported_quality(boundary_polygon, quality):
    with pytest.raises(NotImplementedError):
        triangulate_planar_domain(
            boundary_polygon,
            strategy=ConformingDelaunay(quality),
        )


def test_explicit_frame_preserves_input_coordinates():
    frame = Frame([0, 0, 2], [1, 0, 0], [0, 1, 0])
    boundary = [[0, 0, 2], [2, 0, 2], [2, 2, 2], [0, 2, 2]]
    result = triangulate_planar_domain(boundary, strategy=ConstrainedDelaunay(), frame=frame)

    output = {tuple(point) for point in result.vertices}
    assert all(tuple(point) in output for point in boundary)


def test_planarity_is_validated():
    boundary = [[0, 0, 0], [2, 0, 0], [2, 2, 0.1], [0, 2, 0]]
    with pytest.raises(ValueError, match="world XY"):
        triangulate_planar_domain(boundary, strategy=ConstrainedDelaunay())


def test_native_boundary_sizes_are_validated():
    with pytest.raises(ValueError, match="Delaunay input"):
        triangulate_planar_points([[0, 0, 0], [1, 0, 0]], strategy=Delaunay())
    with pytest.raises(ValueError, match="Boundary"):
        triangulate_planar_domain([[0, 0, 0], [1, 0, 0]], strategy=ConstrainedDelaunay())
    with pytest.raises(ValueError, match="Hole"):
        triangulate_planar_domain(
            [[0, 0, 0], [2, 0, 0], [0, 2, 0]],
            holes=[[[0.5, 0.5, 0], [1.0, 0.5, 0]]],
            strategy=ConstrainedDelaunay(),
        )
