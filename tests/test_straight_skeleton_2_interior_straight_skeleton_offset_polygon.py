from compas.geometry import Polygon
from compas_cgal.straight_skeleton_2 import offset_polygon


def test_offset_polygon():
    points = [
        (-1.91, 3.59, 0.0),
        (-5.53, -5.22, 0.0),
        (-0.39, -1.98, 0.0),
        (2.98, -5.51, 0.0),
        (4.83, -2.02, 0.0),
        (9.70, -3.63, 0.0),
        (12.23, 1.25, 0.0),
        (3.42, 0.66, 0.0),
        (2.92, 4.03, 0.0),
        (-1.91, 3.59, 0.0),
    ]

    offset = 1.5

    # Test inner offset
    offset_polygon_inner = offset_polygon(points, offset)
    assert len(offset_polygon_inner) > 0
    for polygon in offset_polygon_inner:
        assert isinstance(polygon, Polygon)
        assert len(polygon.points) > 0

    # Test outer offset
    offset_polygon_outer = offset_polygon(points, -offset)
    assert len(offset_polygon_outer) > 0
    for polygon in offset_polygon_outer:
        assert isinstance(polygon, Polygon)
        assert len(polygon.points) > 0
