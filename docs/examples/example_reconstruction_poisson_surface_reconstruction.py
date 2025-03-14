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
    # ==============================================================================
    # Input geometry
    # ==============================================================================

    FILE = Path(__file__).parent.parent.parent / "data" / "oni.xyz"

    points = []
    normals = []
    with open(FILE, "r") as f:
        for line in f:
            x, y, z, nx, ny, nz = line.strip().split()
            points.append([float(x), float(y), float(z)])
            normals.append([float(nx), float(ny), float(nz)])

    # ==============================================================================
    # Compute
    # ==============================================================================

    V, F = poisson_surface_reconstruction(points, normals)
    mesh = Mesh.from_vertices_and_faces(V, F)

    R = Rotation.from_axis_and_angle([1, 0, 0], math.radians(90))
    S = Scale.from_factors([10, 10, 10])
    T = R * S

    c = Pointcloud(V)
    c.transform(T)
    mesh.transform(T)
    points, mesh.name = (c, mesh)

    return points, mesh


points, mesh = reconstruction_poisson_surface_reconstruction()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()
viewer.scene.add(points, pointsize=10, pointcolor=(255, 0, 0))
viewer.scene.add(mesh, show_points=False)
viewer.show()
