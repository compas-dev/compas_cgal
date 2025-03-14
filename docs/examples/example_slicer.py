import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Plane, Point, Vector
from compas.geometry import Polyline
from compas_cgal.slicer import slice_mesh
import numpy as np
from line_profiler import profile
from compas_viewer import Viewer
from compas_viewer.config import Config


@profile
def main():
    # Get Mesh from STL
    FILE = Path(__file__).parent.parent.parent / "data" / "3DBenchy.stl"
    benchy = Mesh.from_stl(FILE)

    V, F = benchy.to_vertices_and_faces()

    # Get Slice planes from the bounding box
    bbox = benchy.aabb()
    normal = Vector(0, 0, 1)
    planes = []
    for i in np.linspace(bbox.zmin, bbox.zmax, 50):
        plane = Plane(Point(0, 0, i), normal)
        planes.append(plane)

    # Slice
    slicer_polylines = slice_mesh((V, F), planes)

    # Convert edges to polylines
    polylines = []
    for polyline in slicer_polylines:
        points = []
        for point in polyline:
            points.append(Point(*point))
        polylines.append(Polyline(points))

    return benchy, polylines


mesh, polylines = main()

# ==============================================================================
# Visualize
# ==============================================================================

config = Config()
config.camera.target = [0, 100, 0]
config.camera.position = [0, -75, 50]
config.camera.scale = 10

viewer = Viewer(config=config)

viewer.scene.add(mesh, opacity=0.5, show_lines=False, show_points=False)
for polyline in polylines:
    viewer.scene.add(polyline, linewidth=2, show_points=False)

viewer.show()
