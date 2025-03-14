from compas.geometry import Polygon
from compas.geometry import Point
from compas_viewer import Viewer
from compas_cgal.straight_skeleton_2 import interior_straight_skeleton
from line_profiler import profile


@profile
def main():
    """Compute the interior straight skeleton of a polygon."""

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

    graph = interior_straight_skeleton(polygon)

    return graph


graph = main()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

for edge in graph.edges():
    line = graph.edge_line(edge)
    if graph.edge_attribute(edge, "inner_bisector"):
        viewer.scene.add(line, linecolor=(1.0, 0.0, 0.0), linewidth=2)
    elif graph.edge_attribute(edge, "bisector"):
        viewer.scene.add(line, linecolor=(0.0, 0.0, 1.0))
    else:
        viewer.scene.add(line, linecolor=(0.0, 0.0, 0.0))

viewer.show()
