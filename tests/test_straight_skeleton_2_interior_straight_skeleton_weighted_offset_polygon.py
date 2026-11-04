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
    ]
    distances = [0.1, 0.3, 0.6, 0.1, 0.7, 0.5, 0.2, 0.4, 0.8]
    weights = [1.0 / d for d in distances]
    offset = 1.0

    for signed_offset in (offset, -offset):
        offset_polygons = weighted_offset_polygon(points, signed_offset, weights)

        assert isinstance(offset_polygons, list), "Expected a list of offset polygons"
        assert len(offset_polygons) > 0, "Expected at least one offset polygon"

        for polygon in offset_polygons:
            assert hasattr(polygon, "__iter__"), "Each polygon should be iterable"
            assert len(polygon) > 2, "Each polygon should have at least 3 vertices"
