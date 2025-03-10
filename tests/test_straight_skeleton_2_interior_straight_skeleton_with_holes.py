from compas.geometry import Polygon
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton_with_holes


def test_interior_straight_skeleton_with_holes():
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

    holes = [
        [(0.42, 0.88, 0.0), (1.1, -1.0, 0.0), (-1.97, -0.93, 0.0), (-1.25, 1.82, 0.0)],
        [(4.25, -0.64, 0.0), (2.9, -3.03, 0.0), (2.12, -2.16, 0.0), (2.89, -0.36, 0.0)],
        [(10.6, 0.29, 0.0), (9.48, -1.54, 0.0), (5.48, -1.26, 0.0), (5.98, -0.04, 0.0)],
    ]

    polygon = Polygon(points)
    holes = [Polygon(hole) for hole in holes]
    graph = interior_straight_skeleton_with_holes(polygon, holes)

    # Basic validation
    edges = list(graph.edges())
    vertices = list(graph.nodes())
    assert len(edges) > 0
    assert len(vertices) > 0

    # Check that we have both inner bisectors and boundary edges
    has_inner_bisector = False
    has_boundary = False
    for edge in edges:
        if graph.edge_attribute(edge, "inner_bisector"):
            has_inner_bisector = True
        elif not graph.edge_attribute(edge, "bisector"):
            has_boundary = True
        if has_inner_bisector and has_boundary:
            break

    assert has_inner_bisector
    assert has_boundary
