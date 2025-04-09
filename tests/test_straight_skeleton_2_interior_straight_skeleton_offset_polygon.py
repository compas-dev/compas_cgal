from compas_cgal.straight_skeleton_2 import offset_polygon, offset_polygon_with_holes


def test_offset_polygon_with_holes():
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

    inner = offset_polygon(points, offset)
    outer = offset_polygon(points, -offset)

    assert len(inner) > 0, "Expected at least one inner offset polygon"
    assert len(outer) > 0, "Expected at least one outer offset polygon"

    result = offset_polygon_with_holes(outer[0], inner, -0.1)

    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result), "Each item should be a (boundary, holes) tuple"

    for boundary, holes in result:
        assert hasattr(boundary, "__iter__")
        assert isinstance(holes, list)
        for hole in holes:
            assert hasattr(hole, "__iter__")
