import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Pointcloud
from compas.geometry import Rotation
from compas.geometry import Scale
from compas_cgal.reconstruction import poisson_surface_reconstruction
from compas_viewer import Viewer

FILE = Path(__file__).parent.parent.parent / "data" / "oni.xyz"

points = []
normals = []
with open(FILE, "r") as f:
    for line in f:
        x, y, z, nx, ny, nz = line.strip().split()
        points.append([float(x), float(y), float(z)])
        normals.append([float(nx), float(ny), float(nz)])

V, F = poisson_surface_reconstruction(points, normals)
mesh = Mesh.from_vertices_and_faces(V, F)

R = Rotation.from_axis_and_angle([1, 0, 0], math.radians(90))
S = Scale.from_factors([5, 5, 5])
T = R * S

cloud = Pointcloud(V)
cloud.transform(T)
mesh.transform(T)

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer(width=1600, height=900)

# viewer.renderer.camera.position = [-5, -5, 1.5]
# viewer.renderer.camera.target = [0, 0, 1.5])

viewer.scene.add(mesh, show_points=False)
# viewer.scene.add(cloud)

viewer.show()
