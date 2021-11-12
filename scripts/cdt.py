import numpy as np

from compas_plotters import Plotter
from compas.geometry import Point, Polygon
from compas_cgal._cgal import triangulations

polygon = Polygon.from_sides_and_radius_xy(5, 10)

vertices = np.array([point[:2] for point in polygon.points], dtype=np.float64)
edges = np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], dtype=np.int32)

result = triangulations.constrained_delaunay_triangulation(vertices, edges)

plotter = Plotter()

for face in result:
    triangle = Polygon([Point(vertices[index][0], vertices[index][1], 0.0) for index in face])
    plotter.add(triangle)

plotter.zoom_extents()
plotter.show()
