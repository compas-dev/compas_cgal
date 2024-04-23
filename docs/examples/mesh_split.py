from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Sphere
from compas_cgal.booleans import split_mesh_mesh
from compas_viewer import Viewer

# ==============================================================================
# Make a box and a sphere
# ==============================================================================

box = Box(2)
A = box.to_vertices_and_faces(triangulated=True)

sphere = Sphere(1, point=[1, 1, 1])
B = sphere.to_vertices_and_faces(u=32, v=32, triangulated=True)

# ==============================================================================
# Compute the mesh split
# ==============================================================================

V, F = split_mesh_mesh(A, B)

mesh = Mesh.from_vertices_and_faces(V, F)

# ==============================================================================
# Seperate disjoint faces and visualize
# ==============================================================================

viewer = Viewer()

# viewer.ui.window.viewport.view3d.camera.position = [...]
# viewer.ui.window.viewport.view3d.camera.target = [...]

for color, vertices in zip([Color.blue(), Color.pink()], mesh.connected_vertices()):
    faces = []
    for indices in F:
        if all(index in vertices for index in indices):
            faces.append(indices)
    mesh = Mesh.from_vertices_and_faces(V, faces)
    mesh.remove_unused_vertices()

    viewer.scene.add(mesh, facecolor=color, show_points=False)

viewer.show()
