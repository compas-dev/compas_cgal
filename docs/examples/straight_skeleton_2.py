from compas.geometry import Line
from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton
from compas_viewer import Viewer

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


graph = create_interior_straight_skeleton(points)

# ==============================================================================
# Viz
# ==============================================================================

viewer = Viewer(width=1600, height=900)
for edge in graph.edges():
    line = Line(*graph.edge_coordinates(edge))
    if graph.edge_attribute(edge, "inner_bisector"):
        print(edge, "inner_bisector")
        viewer.add(line, linecolor=(1.0, 0.0, 0.0), linewidth=2)
    elif graph.edge_attribute(edge, "bisector"):
        viewer.add(line, linecolor=(0.0, 0.0, 1.0))
    else:
        viewer.add(line, linecolor=(0.0, 0.0, 0.0))
viewer.show()
