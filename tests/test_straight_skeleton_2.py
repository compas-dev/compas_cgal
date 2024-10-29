from compas_cgal.straight_skeleton_2 import interior_straight_skeleton
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton_with_holes
from compas_cgal.straight_skeleton_2 import offset_polygon
from compas_cgal.straight_skeleton_2 import offset_polygon_with_holes
from compas_cgal.straight_skeleton_2 import weighted_offset_polygon


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
    graph = interior_straight_skeleton(points)
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
    graph = interior_straight_skeleton_with_holes(points, [hole])
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
    polygons = offset_polygon(points, offset)
    assert len(polygons) == 1, len(polygons)
    polygons = offset_polygon(points, -offset)
    assert len(polygons) == 1, len(polygons)
    weights = [0.1, 0.5, 0.3, 0.3, 0.9, 1.0, 0.2, 1.0]
    polygons = weighted_offset_polygon(points, offset, weights)
    assert len(polygons) == 1, len(polygons)
    polygons = weighted_offset_polygon(points, -offset, weights)
    assert len(polygons) == 1, len(polygons)


def test_offset_with_holes():
    points = [
        (65.322, -16.156, 0.0),
        (65.322, -11.157, 0.0),
        (63.022, -11.157, 0.0),
        (63.022, -11.167, 0.0),
        (60.042, -11.167, 0.0),
        (60.042, -16.156, 0.0),
        (61.702, -16.156, 0.0),
        (61.702, -16.416, 0.0),
        (61.712, -16.416, 0.0),
        (61.712, -16.156, 0.0),
    ]
    holes = [
        [
            (63.912, -14.956, 0.0),
            (63.652, -14.956, 0.0),
            (63.652, -14.946, 0.0),
            (61.442, -14.946, 0.0),
            (61.442, -12.367, 0.0),
            (61.702, -12.367, 0.0),
            (61.702, -12.377, 0.0),
            (63.652, -12.377, 0.0),
            (63.652, -12.367, 0.0),
            (63.912, -12.367, 0.0),
            (63.912, -12.834, 0.0),
        ],
        [(61.452, -14.946, 0.0), (61.532, -14.949, 0.0), (61.702, -14.956, 0.0), (61.532, -14.956, 0.0), (61.452, -14.956, 0.0)],
    ]
    result = offset_polygon_with_holes(points, holes, -0.2)
    assert len(result) == 1, len(result)
    polygon, holes = result[0]
    assert len(holes) == 1, len(holes)
    area_net = polygon.area - sum(h.area for h in holes)
    assert abs(area_net - 26.25329) < 1e-3, area_net
