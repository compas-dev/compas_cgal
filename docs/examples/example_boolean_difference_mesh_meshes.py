from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Polyhedron
from compas.geometry import Sphere
from compas_viewer import Viewer

from compas_cgal.booleans import boolean_chain


# =============================================================================
# Classic CSG: rounded cube drilled along three axes.
#   step 1: rounded cube  =  cube  ∩  sphere
#   step 2: result        =  rounded cube  −  cyl_x  −  cyl_y  −  cyl_z
#
# All five meshes are sent to C++ in a single boolean_chain() call. Each
# step's intermediate Surface_mesh stays in C++ — there is no Python ↔ C++
# round-tripping between operations. The chain runs in CGAL's exact-
# constructions kernel (EPECK), which handles the degenerate triple
# intersection at the origin where the three axis-aligned cylinders meet —
# no shifts needed. Pass `hybrid=True` to switch to the hybrid kernel
# scheme (EPICK mesh + EPECK vertex_point_map) from CGAL's "consecutive
# boolean operations with exact point maps" example.
# =============================================================================

cube = Box(2).to_vertices_and_faces(triangulated=True)
sphere = Sphere(1.3, point=[0, 0, 0]).to_vertices_and_faces(u=64, v=64, triangulated=True)


def cylinder_along(axis, radius=0.8):
    """A cylinder of length 4 oriented along a world axis.

    `Cylinder` defines its long axis as the frame's z-axis, so we build a
    frame whose z-axis matches the chosen world axis.
    """
    if axis == "x":
        frame = Frame([0, 0, 0], [0, 1, 0], [0, 0, 1])
    elif axis == "y":
        frame = Frame([0, 0, 0], [0, 0, 1], [1, 0, 0])
    else:  # "z"
        frame = Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
    return Cylinder(radius, 4.0, frame).to_vertices_and_faces(u=48, triangulated=True)


V, F = boolean_chain(
    [cube, sphere, cylinder_along("x"), cylinder_along("y"), cylinder_along("z")],
    ["intersection", "difference", "difference", "difference"],
)
shape = Polyhedron(V.tolist(), F.tolist()).to_mesh()

# =============================================================================
# Visualize
# =============================================================================

viewer = Viewer()
viewer.scene.add(shape, lineswidth=1, show_points=False)
viewer.show()
