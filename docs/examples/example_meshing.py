from pathlib import Path

from compas.datastructures import Mesh
from compas.geometry import Pointcloud
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.scene.tagobject import Tag

from compas_cgal.meshing import trimesh_remesh

# =============================================================================
# Input mesh
# =============================================================================

input_file = Path(__file__).parent.parent.parent / "data" / "rhinovault_mesh_0.ply"

mesh = Mesh.from_ply(input_file)
mesh.quads_to_triangles()

VF = mesh.to_vertices_and_faces()

# =============================================================================
# Footprint bounds + the four base corners
# =============================================================================

coords = mesh.vertices_attributes("xyz")
xmin = min(x for x, _, _ in coords)
xmax = max(x for x, _, _ in coords)
ymin = min(y for _, y, _ in coords)
ymax = max(y for _, y, _ in coords)
zmax = max(z for _, _, z in coords)

# The four base corners: the boundary vertices nearest the xy-extremes of the
# footprint. Their coordinates are what we hand to ``keep_points``.
boundary_xyz = [mesh.vertex_coordinates(v) for v in mesh.vertices_on_boundary()]


def nearest_corner(tx, ty):
    return min(boundary_xyz, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)


corners = [
    nearest_corner(xmin, ymin),
    nearest_corner(xmax, ymin),
    nearest_corner(xmax, ymax),
    nearest_corner(xmin, ymax),
]

# =============================================================================
# Remesh three ways to a coarse target (larger than the input boundary spacing)
# =============================================================================

TARGET_EDGE_LENGTH = 3
ITERATIONS = 10

# 1) Default: the open perimeter is coarsened and its corners rounded.
V0, F0 = trimesh_remesh(VF, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=False)

# 2) protect_boundary=True: every boundary edge is constrained, so the whole
#    perimeter is preserved verbatim while the interior is coarsened.
V1, F1 = trimesh_remesh(VF, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=True)

# 3) keep_points: only the four corners are pinned — the rest of the boundary
#    is still re-sampled, but those four vertices survive exactly.
V2, F2 = trimesh_remesh(VF, TARGET_EDGE_LENGTH, ITERATIONS, keep_points=corners)

# =============================================================================
# Visualize — three panels side by side, each over the faint original
# =============================================================================

dx = 1.3 * (xmax - xmin)  # offset between panels
xmid = 0.5 * (xmin + xmax)

viewer = Viewer(width=1600, height=900)

labels = ["protect_boundary = False", "protect_boundary = True", "keep_points = 4 corners"]
for i, (V, F) in enumerate([(V0, F0), (V1, F1), (V2, F2)]):
    shift = Translation.from_vector([i * dx, 0.0, 0.0])
    remeshed = Mesh.from_vertices_and_faces(V.tolist(), F.tolist()).transformed(shift)
    original = mesh.transformed(shift)
    viewer.scene.add(original, show_points=False, opacity=0.25)
    viewer.scene.add(remeshed, show_points=True)
    viewer.scene.add(Tag(labels[i], (xmid + i * dx, ymin - 2.0, zmax + 1.0), height=30))

# Emphasize the four kept corners on the third panel.
kept = Pointcloud(corners).transformed(Translation.from_vector([2 * dx, 0.0, 0.0]))
viewer.scene.add(kept, pointcolor=(1.0, 0.0, 0.0), pointsize=20, show_points=True)

viewer.show()
