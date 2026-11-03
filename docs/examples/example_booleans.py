from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Native
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.geometry import UVGrid
from compas.geometry import boolean_difference_mesh_mesh
from compas.geometry import boolean_intersection_mesh_mesh
from compas.geometry import boolean_union_mesh_mesh
from compas_viewer import Viewer


def input():
    """Create an input for the boolean methods."""
    box = Box(2)
    A = box.tessellate(Native())
    sphere = Sphere(1, frame=Frame(point=[1, 1, 1]))
    B = sphere.tessellate(UVGrid(64, 64))
    return A, B


def boolean_difference():
    """Compute the boolean difference of two triangle meshes."""
    A, B = input()
    return boolean_difference_mesh_mesh(A, B).to_mesh()


def boolean_intersection():
    """Compute the boolean intersection of two triangle meshes."""
    A, B = input()
    return boolean_intersection_mesh_mesh(A, B).to_mesh()


def boolean_union():
    """Compute the boolean union of two triangle meshes."""
    A, B = input()
    return boolean_union_mesh_mesh(A, B).to_mesh()


# =============================================================================
# Booleans
# =============================================================================

difference = boolean_difference()
intersection = boolean_intersection()
union = boolean_union()

# =============================================================================
# Spread
# =============================================================================

difference.transform(Translation.from_vector([-6, 0, 0]))
intersection.transform(Translation.from_vector([-2, 0, 0]))
union.transform(Translation.from_vector([2, 0, 0]))


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.scene.add(difference, lineswidth=1, show_points=False)
viewer.scene.add(intersection, lineswidth=1, show_points=False)
viewer.scene.add(union, lineswidth=1, show_points=False)

viewer.show()
