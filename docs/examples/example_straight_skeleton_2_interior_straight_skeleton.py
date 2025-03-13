from compas_cgal.straight_skeleton_2 import interior_straight_skeleton
from compas_viewer import Viewer
from line_profiler import profile


@profile
def main():
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

    return graph


if __name__ == "__main__":
    graph = main()
    # ==============================================================================
    # Viz
    # ==============================================================================

    viewer = Viewer(width=1600, height=900)
    for edge in graph.edges():
        line = graph.edge_line(edge)
        if graph.edge_attribute(edge, "inner_bisector"):
            print(edge, "inner_bisector")
            viewer.scene.add(line, linecolor=(1.0, 0.0, 0.0), linewidth=2)
        elif graph.edge_attribute(edge, "bisector"):
            viewer.scene.add(line, linecolor=(0.0, 0.0, 1.0))
        else:
            viewer.scene.add(line, linecolor=(0.0, 0.0, 0.0))
    viewer.show()
