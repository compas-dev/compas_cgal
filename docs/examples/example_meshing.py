from pathlib import Path

from compas.datastructures import Mesh
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
# Remesh — default vs. protected boundary
# =============================================================================

# A coarse target (larger than the input boundary spacing) makes the effect of
# ``protect_boundary`` visible: the default pass re-samples the open perimeter,
# while the protected pass keeps every boundary edge.
TARGET_EDGE_LENGTH = 3
ITERATIONS = 10

# Default: the shell's open perimeter is coarsened and its corners rounded.
V0, F0 = trimesh_remesh(VF, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=False)

# protect_boundary=True: every boundary edge is constrained, so the supported
# perimeter is preserved verbatim while the interior is coarsened.
V1, F1 = trimesh_remesh(VF, TARGET_EDGE_LENGTH, ITERATIONS, protect_boundary=True)

remeshed_free = Mesh.from_vertices_and_faces(V0, F0)
remeshed_protected = Mesh.from_vertices_and_faces(V1, F1)

# =============================================================================
# Visualize — the two results side by side, each over the original (faint)
# =============================================================================

coords = mesh.vertices_attributes("xyz")
xmin = min(x for x, _, _ in coords)
xmax = max(x for x, _, _ in coords)
ymin = min(y for _, y, _ in coords)
zmax = max(z for _, _, z in coords)

dx = 1.3 * (xmax - xmin)  # offset the second panel clear of the first
xmid = 0.5 * (xmin + xmax)

shift = Translation.from_vector([dx, 0.0, 0.0])
remeshed_protected.transform(shift)
mesh_right = mesh.transformed(shift)

viewer = Viewer(width=1600, height=900)

# Left: protect_boundary=False — perimeter coarsened, corners rounded.
viewer.scene.add(mesh, show_points=False, opacity=0.25)
viewer.scene.add(remeshed_free, show_points=True)
viewer.scene.add(Tag("protect_boundary = False", (xmid, ymin - 2.0, zmax + 1.0), height=30))

# Right: protect_boundary=True — perimeter preserved.
viewer.scene.add(mesh_right, show_points=False, opacity=0.25)
viewer.scene.add(remeshed_protected, show_points=True)
viewer.scene.add(Tag("protect_boundary = True", (xmid + dx, ymin - 2.0, zmax + 1.0), height=30))

viewer.show()
