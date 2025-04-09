from compas.geometry import Polygon
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton_with_holes


def test_interior_straight_skeleton_with_holes():
    # Outer boundary
    points_boundary = [
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
    boundary = Polygon(points_boundary)

    # Inner holes
    holes = [
        [(0.42, 0.88, 0.0), (1.1, -1.0, 0.0), (-1.97, -0.93, 0.0), (-1.25, 1.82, 0.0)],
        [(4.25, -0.64, 0.0), (2.9, -3.03, 0.0), (2.12, -2.16, 0.0), (2.89, -0.36, 0.0)],
        [(10.6, 0.29, 0.0), (9.48, -1.54, 0.0), (5.48, -1.26, 0.0), (5.98, -0.04, 0.0)],
    ]
    holes = [Polygon(hole) for hole in holes]

    # Run the function
    graph = interior_straight_skeleton_with_holes(boundary, holes)

    # Assertions
    assert graph is not None, "Expected a graph object"
    assert graph.number_of_edges() > 0, "Graph should have at least one edge"
    assert graph.number_of_nodes() > 0, "Graph should have at least one node"

    for u, v in graph.edges():
        line = graph.edge_line((u, v))
        assert line, f"Edge {u}-{v} should have a line geometry"
        assert hasattr(line, "length"), "Line object should have a length attribute"
