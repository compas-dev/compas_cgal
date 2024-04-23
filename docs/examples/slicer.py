from pathlib import Path

import numpy as np
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Vector
from compas_cgal.slicer import slice_mesh_planes
from compas_viewer import Viewer

FILE = Path(__file__).parent.parent.parent / "data" / "3DBenchy.stl"

# ==============================================================================
# Get benchy and construct a mesh
# ==============================================================================

benchy = Mesh.from_stl(FILE)

# ==============================================================================
# Create planes
# ==============================================================================

# replace by planes along a curve

bbox = benchy.aabb()

normal = Vector(0, 0, 1)
planes = []
for i in np.linspace(bbox.zmin, bbox.zmax, 50):
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

viewer = Viewer(width=1600, height=900)

# viewer.view.camera.position = [-40, -70, 40]
# viewer.view.camera.look_at([0, 0, 20])

viewer.scene.add(benchy, show_lines=False, show_points=False, opacity=0.5)

for polyline in polylines:
    viewer.scene.add(polyline, linecolor=Color.grey(), linewidth=2, show_points=False)

viewer.show()
