from compas.geometry import Polygon
from compas_viewer import Viewer

from compas_cgal.straight_skeleton_2 import offset_polygon
from compas_cgal.straight_skeleton_2 import offset_polygon_with_holes


def main():
    """Create offset polygons."""

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
    polygon = Polygon(points)
    offset = 1.5

    offset_polygon_inner = offset_polygon(points, offset)
    offset_polygon_outer = offset_polygon(points, -offset)


    result = offset_polygon_with_holes(offset_polygon_outer[0], offset_polygon_inner, -0.1)


    return offset_polygon_inner, offset_polygon_outer, polygon, result


offset_polygon_inner, offset_polygon_outer, polygon, result = main()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()
viewer.scene.add(polygon, show_faces=False)
viewer.config.renderer.show_grid = False

for opolygon in offset_polygon_inner:
    viewer.scene.add(opolygon, linecolor=(1.0, 0.0, 0.0), facecolor=(1.0, 0.0, 0.0, 0.0), show_faces=False)

for opolygon in offset_polygon_outer:
    viewer.scene.add(opolygon, linecolor=(0.0, 0.0, 1.0), facecolor=(0.0, 0.0, 1.0, 0.0), show_faces=False)

for opolygon, holes in result:
    viewer.scene.add(opolygon, linecolor=(0.0, 0.0, 1.0), facecolor=(0.0, 0.0, 1.0, 0.0), show_faces=False)
    for hole in holes:
        viewer.scene.add(hole, linecolor=(0.0, 0.0, 1.0), facecolor=(0.0, 0.0, 1.0, 0.0), show_faces=False)

viewer.show()