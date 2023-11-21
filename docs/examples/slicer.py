from pathlib import Path
import numpy as np

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Polyline
from compas.datastructures import Mesh
from compas.colors import Color
from compas_view2.app import App

from compas_cgal.slicer import slice_mesh_planes

FILE = Path(__file__).parent.parent.parent / "data" / "3DBenchy.stl"

# ==============================================================================
# Get benchy and construct a mesh
# ==============================================================================

benchy = Mesh.from_stl(FILE)

# ==============================================================================
# Create planes
# ==============================================================================

# replace by planes along a curve

bbox = benchy.bounding_box()

x, y, z = zip(*bbox)
zmin, zmax = min(z), max(z)

normal = Vector(0, 0, 1)
planes = []
for i in np.linspace(zmin, zmax, 50):
    plane = Plane(Point(0, 0, i), normal)
    planes.append(plane)

# ==============================================================================
# Slice
# ==============================================================================

M = benchy.to_vertices_and_faces()

pointsets = slice_mesh_planes(M, planes)

# ==============================================================================
# Process output
# ==============================================================================

polylines = []
for points in pointsets:
    points = [Point(*point) for point in points]
    polyline = Polyline(points)
    polylines.append(polyline)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [-40, -70, 40]
viewer.view.camera.look_at([0, 0, 20])

viewer.add(benchy, show_lines=False, opacity=0.5)

for polyline in polylines:
    viewer.add(polyline, linecolor=Color.grey(), linewidth=2)

viewer.run()
