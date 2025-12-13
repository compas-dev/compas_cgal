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

params = [
    (20.0, 30.0, 0.375),      # base
    (10.0, 15.0, 0.1875),     # / 2
    (5.0, 7.5, 0.09375),      # / 4
]

meshes = []
offset = 0.0
for sm_angle, sm_radius, sm_distance in params:
    V, F = poisson_surface_reconstruction(
        points,
        normals,
        sm_angle=sm_angle,
        sm_radius=sm_radius,
        sm_distance=sm_distance,
    )
    mesh = Mesh.from_vertices_and_faces(V, F)
    mesh.translate([offset, 0, 0])
    meshes.append(mesh)
    offset += 1

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0.5, 0, 0]
viewer.renderer.camera.position = [0.5, -0.2, 2.0]

for mesh in meshes:
    viewer.scene.add(mesh, show_points=False)

viewer.show()
