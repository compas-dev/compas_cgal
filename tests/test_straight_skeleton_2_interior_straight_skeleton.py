from compas.geometry import Point, Polygon
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton


def test_interior_straight_skeleton():
    # Define polygon points
    points = [
        Point(-1.91, 3.59, 0.0),
        Point(-5.53, -5.22, 0.0),
        Point(-0.39, -1.98, 0.0),
        Point(2.98, -5.51, 0.0),
        Point(4.83, -2.02, 0.0),
        Point(9.70, -3.63, 0.0),
        Point(12.23, 1.25, 0.0),
        Point(3.42, 0.66, 0.0),
        Point(2.92, 4.03, 0.0),
        Point(-1.91, 3.59, 0.0),
    ]
    polygon = Polygon(points)

    # Compute skeleton
    graph = interior_straight_skeleton(polygon)

    # Assertions
    assert graph is not None, "Expected a graph object"
    assert graph.number_of_nodes() > 0, "Graph should have nodes"
    assert graph.number_of_edges() > 0, "Graph should have edges"

    for edge in graph.edges():
        line = graph.edge_line(edge)
        assert line, f"Edge {edge} should return a valid line"
        assert hasattr(line, "length"), "Line should have a length attribute"
        length = line.length
        assert length > 0, "Skeleton edge line should have positive length"
