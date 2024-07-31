from compas.geometry import Polygon, Line
from compas_viewer import Viewer

from compas_cgal.straight_skeleton_2 import create_interior_straight_skeleton_with_holes

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
graph = create_interior_straight_skeleton_with_holes(polygon, holes)

# ==============================================================================
# Viz
# ==============================================================================

viewer = Viewer(width=1600, height=900)

for edge in graph.edges():
    line = Line(*graph.edge_coordinates(edge))
    if graph.edge_attribute(edge, "inner_bisector"):
        viewer.add(line, linecolor=(1.0, 0.0, 0.0), linewidth=2)
    elif graph.edge_attribute(edge, "bisector"):
        viewer.add(line, linecolor=(0.0, 0.0, 1.0))
    else:
        viewer.add(line, linecolor=(0.0, 0.0, 0.0))
viewer.show()
