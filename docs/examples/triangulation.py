import numpy as np

from compas_plotters import Plotter
from compas.geometry import Polygon, Translation
from compas.datastructures import Mesh
from compas_cgal.triangulation import constrained_delaunay_triangulation

# ==============================================================================
# Constraints
# ==============================================================================

boundary = Polygon.from_sides_and_radius_xy(4, 10)
boundary = np.array(boundary, dtype=np.float64)

hole = Polygon.from_sides_and_radius_xy(8, 2)

hole1 = hole.transformed(Translation.from_vector([4, 0, 0]))
hole2 = hole.transformed(Translation.from_vector([-4, 0, 0]))
hole3 = hole.transformed(Translation.from_vector([0, 4, 0]))
hole4 = hole.transformed(Translation.from_vector([0, -4, 0]))

holes = [hole1, hole2, hole3, hole4]

# ==============================================================================
# Triangulation
# ==============================================================================

V, F = constrained_delaunay_triangulation(boundary, holes, maxlength=1.0)

mesh = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Viz
# ==============================================================================

plotter = Plotter(figsize=(8, 8))
plotter.add(mesh, sizepolicy='absolute', vertexsize=5)
plotter.zoom_extents()
plotter.show()
