from compas.geometry import Box
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas_viewer import Viewer
from line_profiler import profile

from compas_cgal.subdivision import mesh_subdivide_catmull_clark
from compas_cgal.subdivision import mesh_subdivide_loop
from compas_cgal.subdivision import mesh_subdivide_sqrt3


@profile
def main():
    """Subdivide a mesh using different subdivision algorithms."""

    # ==============================================================================
    # Input geometry
    # ==============================================================================

    box = Box.from_diagonal(([0, 0, 0], [1, 1, 1]))

    V0, F0 = box.to_vertices_and_faces(triangulated=False)
    V1, F1 = box.to_vertices_and_faces(triangulated=False)
    V2, F2 = box.to_vertices_and_faces(triangulated=True)
    V3, F3 = box.to_vertices_and_faces(triangulated=True)

    # ==============================================================================
    # Compute
    # ==============================================================================

    V4, F4 = mesh_subdivide_catmull_clark((V1, F1), 3)
    V5, F5 = mesh_subdivide_loop((V2, F2), 3)
    V6, F6 = mesh_subdivide_sqrt3((V3, F3), 3)

    S2 = Polyhedron(V0, F0)
    S4 = Polyhedron(V4.tolist(), F4.tolist())
    S6 = Polyhedron(V5.tolist(), F5.tolist())
    S8 = Polyhedron(V6.tolist(), F6.tolist())

    S2.transform(Translation.from_vector([1, 0, 0]))
    S4.transform(Translation.from_vector([2, 0, 0]))
    S6.transform(Translation.from_vector([3, 0, 0]))
    S8.transform(Translation.from_vector([4, 0, 0]))

    # ==============================================================================
    # Visualize
    # ==============================================================================

    return S2, S4, S6, S8


S2, S4, S6, S8 = main()


# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [3, 1, 0.5]
viewer.renderer.camera.position = [5, -2, 0.5]

viewer.scene.add(S2.to_mesh(), show_points=False)
viewer.scene.add(S4.to_mesh(), show_points=False)
viewer.scene.add(S6.to_mesh(), show_points=False)
viewer.scene.add(S8.to_mesh(), show_points=False)

viewer.show()
