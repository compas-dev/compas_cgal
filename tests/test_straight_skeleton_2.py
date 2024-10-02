from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton
from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton_with_holes
from compas_cgal.straight_skeleton_2 import create_offset_polygons_2
from compas_cgal.straight_skeleton_2 import create_weighted_offset_polygons_2


def test_straight_polygon():
    points = [
        (-1, -1, 0),
        (0, -12, 0),
        (1, -1, 0),
        (12, 0, 0),
        (1, 1, 0),
        (0, 12, 0),
        (-1, 1, 0),
        (-12, 0, 0),
    ]
    graph = create_interior_straight_skeleton(points)
    assert graph.number_of_edges() == 16


def test_straight_skeleton_with_holes():
    points = [
        (-1, -1, 0),
        (0, -12, 0),
        (1, -1, 0),
        (12, 0, 0),
        (1, 1, 0),
        (0, 12, 0),
        (-1, 1, 0),
        (-12, 0, 0),
    ]
    hole = [(-1, 0, 0), (0, 1, 0), (1, 0, 0), (0, -1, 0)]
    graph = create_interior_straight_skeleton_with_holes(points, [hole])
    assert graph.number_of_edges() == 32


def test_offset():
    points = [
        (-1, -1, 0),
        (0, -12, 0),
        (1, -1, 0),
        (12, 0, 0),
        (1, 1, 0),
        (0, 12, 0),
        (-1, 1, 0),
        (-12, 0, 0),
    ]
    offset = 0.5
    polygons = create_offset_polygons_2(points, offset)
    assert len(polygons) == 1, len(polygons)
    polygons = create_offset_polygons_2(points, -offset)
    assert len(polygons) == 1, len(polygons)
    weights = [0.1, 0.5, 0.3, 0.3, 0.9, 1.0, 0.2, 1.0]
    polygons = create_weighted_offset_polygons_2(points, offset, weights)
    assert len(polygons) == 1, len(polygons)
    polygons = create_weighted_offset_polygons_2(points, -offset, weights)
    assert len(polygons) == 1, len(polygons)
