import pytest
import numpy as np
from compas.geometry import Polygon
from compas.geometry import Translation
from compas_cgal.triangulation import delaunay_triangulation
from compas_cgal.triangulation import conforming_delaunay_triangulation
from compas_cgal.triangulation import refined_delaunay_mesh


@pytest.fixture
def boundary_polygon():
    """Create a square boundary polygon."""
    return Polygon.from_sides_and_radius_xy(64, 4)


@pytest.fixture
def hole_polygons():
    """Create four circular holes in the boundary."""
    hole = Polygon.from_sides_and_radius_xy(128, 1)
    hole1 = hole.transformed(Translation.from_vector([2, 0, 0]))
    hole2 = hole.transformed(Translation.from_vector([-2, 0, 0]))
    hole3 = hole.transformed(Translation.from_vector([0, 2, 0]))
    hole4 = hole.transformed(Translation.from_vector([0, -2, 0]))
    return [hole1, hole2, hole3, hole4]


def test_delaunay_triangulation(boundary_polygon):
    """Test basic Delaunay triangulation of points."""
    points = np.array(boundary_polygon.points)
    F = delaunay_triangulation(points)

    assert isinstance(F, np.ndarray)
    assert F.shape[1] == 3  # triangles
    assert len(F) > 0


def test_conforming_delaunay_triangulation(boundary_polygon, hole_polygons):
    """Test constrained Delaunay triangulation with holes."""
    V, F = conforming_delaunay_triangulation(
        boundary_polygon,
        holes=hole_polygons,
    )

    assert isinstance(V, np.ndarray)
    assert isinstance(F, np.ndarray)
    assert V.shape[1] == 3  # 3D points
    assert F.shape[1] == 3  # triangles
    assert len(V) > 0
    assert len(F) > 0

    # Check that we have more vertices than the input due to conforming constraints
    input_points = len(boundary_polygon.points) + sum(len(h.points) for h in hole_polygons)
    assert len(V) >= input_points


def test_refined_delaunay_mesh(boundary_polygon, hole_polygons):
    """Test refined Delaunay mesh with quality constraints."""
    maxlength = 0.5
    V, F = refined_delaunay_mesh(
        boundary_polygon,
        holes=hole_polygons,
        maxlength=maxlength,
        is_optimized=True,
    )

    assert isinstance(V, np.ndarray)
    assert isinstance(F, np.ndarray)
    assert V.shape[1] == 3  # 3D points
    assert F.shape[1] == 3  # triangles
    assert len(V) > 0
    assert len(F) > 0

    # Check refinement created more vertices than CDT
    V_cdt, _ = conforming_delaunay_triangulation(boundary_polygon, holes=hole_polygons)
    assert len(V) > len(V_cdt)

    # Check edge lengths
    edges = []
    for face in F:
        for i in range(3):
            edge = sorted([face[i], face[(i + 1) % 3]])
            if edge not in edges:
                edges.append(edge)

    for v1, v2 in edges:
        edge_length = np.linalg.norm(V[v1] - V[v2])
        assert edge_length <= maxlength * 1.1  # Allow 10% tolerance
