from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Sphere
from compas_viewer import Viewer

from compas_cgal.booleans import boolean_chain_with_face_source


# =============================================================================
# Same CSG as example_boolean_difference_mesh_meshes.py, but every output face
# is colored by which input mesh it descended from.
#
#     result = cube ∩ sphere − cyl_x − cyl_y − cyl_z
#
# All five input meshes go to C++ in a single boolean_chain_with_face_source
# call. A CGAL corefinement visitor propagates a per-face tag through every
# step so every output triangle carries [mesh_id, face_id] of its origin.
#
# The default kernel is EPECK (exact=True). Constructions are computed in
# CGAL's Exact_predicates_exact_constructions_kernel, which handles the
# degenerate triple intersection where the three axis-aligned cylinders meet
# at the origin without any geometric workarounds. Set exact=False to use
# EPICK, in which case the cylinders should be shifted by a sub-millimetre
# amount to avoid the "Non-handled triple intersection" precondition.
# =============================================================================

cube = Box(2).to_vertices_and_faces(triangulated=True)
sphere = Sphere(1.3, point=[0, 0, 0]).to_vertices_and_faces(u=64, v=64, triangulated=True)


def cylinder_along(axis, radius=0.8):
    """Cylinder of length 4 along a world axis, centred at the origin."""
    if axis == "x":
        frame = Frame([0, 0, 0], [0, 1, 0], [0, 0, 1])
    elif axis == "y":
        frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
    else:  # "z"
        frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    return Cylinder(radius, 4.0, frame).to_vertices_and_faces(u=48, triangulated=True)


cyl_x = cylinder_along("x")
cyl_y = cylinder_along("y")
cyl_z = cylinder_along("z")

V, F, S = boolean_chain_with_face_source(
    [cube, sphere, cyl_x, cyl_y, cyl_z],
    ["intersection", "difference", "difference", "difference"],
    exact=False,
)

mesh = Mesh.from_vertices_and_faces(V, F)

# =============================================================================
# Color the output by source mesh:
#   mesh_id == 0  -> cube     (red)
#   mesh_id == 1  -> sphere   (blue)        — rounded corners/edges
#   mesh_id == 2  -> cyl_x    (green)       — X-axis through-hole walls
#   mesh_id == 3  -> cyl_y    (yellow)      — Y-axis through-hole walls
#   mesh_id == 4  -> cyl_z    (magenta)     — Z-axis through-hole walls
# =============================================================================

palette = {
    0: Color(0.85, 0.30, 0.30),
    1: Color(0.30, 0.50, 0.85),
    2: Color(0.40, 0.80, 0.40),
    3: Color(0.95, 0.85, 0.30),
    4: Color(0.80, 0.40, 0.85),
}

facecolor = {fkey: palette[mesh_id] for fkey, (mesh_id, _) in zip(mesh.faces(), S.tolist())}

# =============================================================================
# Visualize
# =============================================================================

viewer = Viewer()
viewer.scene.add(mesh, facecolor=facecolor, lineswidth=1, show_points=False, show_lines=True)
viewer.show()
