from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Line
from compas.geometry import Sphere
from compas_viewer import Viewer

from compas_cgal.booleans import boolean_difference_mesh_mesh_with_edges


def input():
    """Two triangle meshes that intersect."""
    A = Box(2).to_vertices_and_faces(triangulated=True)
    B = Sphere(1, point=[1, 1, 1]).to_vertices_and_faces(u=64, v=64, triangulated=True)
    return A, B


# =============================================================================
# Boolean difference with intersection-curve edges
# =============================================================================

A, B = input()
V, F, E = boolean_difference_mesh_mesh_with_edges(A, B)

mesh = Mesh.from_vertices_and_faces(V, F)
intersection_lines = [Line(V[i], V[j]) for i, j in E.tolist()]

# =============================================================================
# Visualize
# =============================================================================

viewer = Viewer()
viewer.scene.add(mesh, lineswidth=1, show_points=False)
group = viewer.scene.add_group(name="Intersection curve")
group.add_from_list(intersection_lines, linewidth=3, linecolor=(1.0, 0.0, 0.0))

viewer.show()
