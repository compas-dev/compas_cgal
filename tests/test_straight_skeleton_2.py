from compas.tolerance import TOL

from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton
from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton_with_holes


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
    lines = create_interior_straight_skeleton_with_holes(points, [hole])
    assert len(lines) == 20


def test_straight_polygon_2_compare():
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
    lines = create_interior_straight_skeleton(points)

    expected = [
        [[-1.91, 3.59, 0.0], [-0.139446292, 1.191439787, 0.0]],
        [[-5.53, -5.22, 0.0], [-0.139446292, 1.191439787, 0.0]],
        [[-0.39, -1.98, 0.0], [0.008499564, 1.241560466, 0.0]],
        [[2.98, -5.51, 0.0], [2.44972507, -1.674799065, 0.0]],
        [[4.83, -2.02, 0.0], [4.228131167, -0.522007766, 0.0]],
        [[8.663865218, -1.084821998, 0.0], [9.7, -3.63, 0.0]],
        [[12.23, 1.25, 0.0], [8.663865218, -1.084821998, 0.0]],
        [[3.42, 0.66, 0.0], [1.755862468, -1.404991433, 0.0]],
        [[2.92, 4.03, 0.0], [0.563706846, 1.033296141, 0.0]],
        [[4.228131167, -0.522007766, 0.0], [2.44972507, -1.674799065, 0.0]],
        [[4.228131167, -0.522007766, 0.0], [8.663865218, -1.084821998, 0.0]],
        [[1.755862468, -1.404991433, 0.0], [2.44972507, -1.674799065, 0.0]],
        [[0.563706846, 1.033296141, 0.0], [1.755862468, -1.404991433, 0.0]],
        [[-0.139446292, 1.191439787, 0.0], [0.008499564, 1.241560466, 0.0]],
        [[0.563706846, 1.033296141, 0.0], [0.008499564, 1.241560466, 0.0]],
    ]
    for act, exp in zip(lines, expected):
        sa, ea = act
        se, ee = exp
        # the line direction sometimes changes ...
        assert TOL.is_allclose(sa, se) or TOL.is_allclose(sa, ee)
        assert TOL.is_allclose(ea, ee) or TOL.is_allclose(ea, se)
