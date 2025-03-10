from compas_cgal.straight_skeleton_2 import weighted_offset_polygon


def test_weighted_offset_polygon():
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

    distances = [0.1, 0.3, 0.6, 0.1, 0.7, 0.5, 0.2, 0.4, 0.8, 0.2]
    weights = [1.0 / d for d in distances]
    offset = 1.0
    offset_polygons_outer = weighted_offset_polygon(points, -offset, weights)

    assert len(offset_polygons_outer) == 1
