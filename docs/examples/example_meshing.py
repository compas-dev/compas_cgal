import numpy as np
from compas.colors import Color
from compas.colors import ColorMap
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Translation
from compas.geometry import distance_point_point
from compas_viewer import Viewer
from compas_viewer.config import Config
from compas_viewer.scene.tagobject import Tag

from compas_cgal.meshing import trimesh_remesh
from compas_cgal.triangulation import refined_delaunay_mesh

# =============================================================================
# Input mesh — a dense 7-lobe star disk (smooth sinusoidal rim)
# =============================================================================
# A star rim exaggerates what ``protect_boundary`` does: the high-curvature
# lobes make a coarse perimeter read as visibly faceted.

N = 300
theta = np.linspace(0.0, 2.0 * np.pi, N, endpoint=False)
radius = 5.0 + 1.5 * np.sin(7.0 * theta)
boundary = [Point(float(r * np.cos(a)), float(r * np.sin(a)), 0.0) for r, a in zip(radius, theta)]

# Triangulate the star into a dense mesh (its perimeter is finely sampled).
V, F = refined_delaunay_mesh(boundary, maxlength=0.25, is_optimized=True)
subdivided = (V, F)

# =============================================================================
# Remesh at a target COARSER than the perimeter sampling
# =============================================================================

TARGET_EDGE_LENGTH = 1.5
ITERATIONS = 10

# protect_boundary=False: the dense perimeter is re-sampled to the target.
V_off, F_off = trimesh_remesh(subdivided, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=False)

# protect_boundary=True: the perimeter density is maintained.
V_on, F_on = trimesh_remesh(subdivided, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=True)

# =============================================================================
# Visualize — two panels side by side, false-colored by local vertex density
# =============================================================================

DX = 15.0  # x-offset between the two panels (the star is ~13 wide)


def at(V, F, dx):
    remeshed = Mesh.from_vertices_and_faces(V.tolist(), F.tolist())
    remeshed.transform(Translation.from_vector([dx, 0.0, 0.0]))
    return remeshed


def vertex_density(mesh):
    """Local density = 1 / shortest incident edge (nearest-neighbour spacing).

    Using the shortest edge (not the mean) keeps a dense-rim vertex hot even
    where it also touches long interior edges — so the maintained perimeter
    reads as a crisp band rather than blending into the coarse interior.
    """
    density = {}
    for v in mesh.vertices():
        p = mesh.vertex_coordinates(v)
        lengths = [distance_point_point(p, mesh.vertex_coordinates(n)) for n in mesh.vertex_neighbors(v)]
        density[v] = 1.0 / min(lengths) if lengths else 0.0
    return density


mesh_off = at(V_off, F_off, 0.0)
mesh_on = at(V_on, F_on, DX)

density_off = vertex_density(mesh_off)
density_on = vertex_density(mesh_on)

# Shared color scale across BOTH meshes so the maintained perimeter reads as
# denser than anything on the unprotected star.
all_density = list(density_off.values()) + list(density_on.values())
dmin, dmax = min(all_density), max(all_density)
cmap = ColorMap.from_two_colors(Color.blue(), Color.red())


def density_colors(mesh, density):
    return {v: cmap(density[v], minval=dmin, maxval=dmax) for v in mesh.vertices()}


config = Config()
config.renderer.show_grid = False  # clean background — no grid/axes distraction
config.camera.target = [DX / 2.0, 0.0, 0.0]
config.camera.position = [DX / 2.0, -3.0, 30.0]  # near top-down

viewer = Viewer(config=config)

# Left: protect_boundary=False — uniformly coarse (cold everywhere).
viewer.scene.add(mesh_off, show_points=False, use_vertexcolors=True, vertexcolor=density_colors(mesh_off, density_off))

# Right: protect_boundary=True — a hot band of maintained density hugs the rim.
viewer.scene.add(mesh_on, show_points=False, use_vertexcolors=True, vertexcolor=density_colors(mesh_on, density_on))

# Label each panel so the difference is explicit in the viewer.
viewer.scene.add(Tag("protect_boundary = False", (0.0, 8.5, 0.0), height=34))
viewer.scene.add(Tag("protect_boundary = True", (DX, 8.5, 0.0), height=34))

viewer.show()
