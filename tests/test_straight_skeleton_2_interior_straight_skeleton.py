from compas_cgal.straight_skeleton_2 import interior_straight_skeleton


def test_interior_straight_skeleton():
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

    graph = interior_straight_skeleton(points)

    # Basic validation
    edges = list(graph.edges())
    vertices = list(graph.nodes())
    assert len(edges) > 0
    assert len(vertices) > 0

    # Check that we have some inner bisectors
    has_inner_bisector = False
    for edge in edges:
        if graph.edge_attribute(edge, "inner_bisector"):
            has_inner_bisector = True
            break
    assert has_inner_bisector
