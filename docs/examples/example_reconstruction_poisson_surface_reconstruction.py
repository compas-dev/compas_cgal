import math
from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Pointcloud
from compas.geometry import Rotation
from compas.geometry import Scale
from compas_cgal.reconstruction import poisson_surface_reconstruction
from compas_viewer import Viewer
from line_profiler import profile


@profile
def reconstruction_poisson_surface_reconstruction():
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

    c = Pointcloud(V)

    return c, mesh


points, mesh = reconstruction_poisson_surface_reconstruction()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.2, 2.0]

viewer.scene.add(points, pointsize=10, pointcolor=(255, 0, 0))
viewer.scene.add(mesh, show_points=False)

viewer.show()
