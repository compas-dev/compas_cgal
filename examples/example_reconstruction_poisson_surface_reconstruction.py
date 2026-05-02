from pathlib import Path

from compas.datastructures import Mesh
from compas_viewer import Viewer

from compas_cgal.reconstruction import poisson_surface_reconstruction

# =============================================================================
# Input
# =============================================================================

FILE = Path(__file__).parent.parent.parent / "data" / "oni.xyz"

points = []
normals = []
with open(FILE, "r") as f:
    for line in f:
        x, y, z, nx, ny, nz = line.strip().split()
        points.append([float(x), float(y), float(z)])
        normals.append([float(nx), float(ny), float(nz)])

# =============================================================================
# Reconstruction
# =============================================================================

# Reconstruct surface with custom parameters
# Using larger sm_radius and sm_distance values reduces mesh complexity
# and helps filter out vertices that don't belong to the original point cloud
V, F = poisson_surface_reconstruction(
    points,
    normals,
    sm_angle=20.0,  # Surface meshing angle bound (degrees)
    sm_radius=30.0,  # Surface meshing radius bound (factor of avg spacing)
    sm_distance=0.375,  # Surface meshing distance bound (factor of avg spacing)
)
mesh = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -0.2, 2.0]

viewer.scene.add(points, pointsize=10, pointcolor=(255, 0, 0))
viewer.scene.add(mesh, show_points=False)

viewer.show()
