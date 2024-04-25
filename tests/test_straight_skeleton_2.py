from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton


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
    lines = create_interior_straight_skeleton(points)
    assert len(lines) == 8
